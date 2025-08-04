import streamlit as st
from gnews import GNews
import re
from datetime import datetime

st.set_page_config(page_title="Jerry Moran News Search", page_icon="📰")

st.title("📰 Jerry Moran News Search")
st.write("Search for news articles about Senator Jerry Moran with multiple search variations")

# Sidebar for inputs
st.sidebar.header("Search Parameters")

# Time range selection
days = st.sidebar.selectbox(
    "Time Range:",
    [1, 3, 7, 14, 30],
    index=1,  # Default to 3 days
    help="How many days back to search"
)

# Filter options
exclude_gov = st.sidebar.checkbox("Exclude .gov sources", value=True)
exclude_quiver = st.sidebar.checkbox("Exclude Quiver Quantitative", value=True)

# Kansas outlets list
kansas_outlets = [
    'Kansas Reflector',
    'The Topeka Capital-Journal',
    'The Wichita Eagle',
    'KCLY Radio',
    'KSN-TV',
    'KWCH',
    'Kansas City Star',
    'Lawrence Journal-World',
    'The Garden City Telegram',
    'KSNT 27 News',
    'The Hutchinson News',
    'Salina Journal',
    'Hays Daily News',
    'Hays Post',
    'Emporia Gazette',
    'JC Post',
    'WIBW'
]

def clean_text(text):
    """Clean text for safe display"""
    text = re.sub(r'[^\w\s\-\.\,\:\;\!\?\(\)\'\"]+', '', text)
    return text.strip()

def search_jerry_moran_news(days, exclude_gov, exclude_quiver):
    """Search for Jerry Moran news with multiple search variations"""
    google_news = GNews()
    google_news.period = f'{days}d'
    google_news.results = 100
    google_news.country = 'US'
    google_news.language = 'en'

    # All search terms
    search_terms = [
        "Jerry Moran",
        "Senator Jerry Moran",
        "Senator Moran",
        "Sen. Moran",
        "Sen. Jerry Moran",
        "Sens. Moran",
        "Sens. Jerry Moran"
    ]

    all_entries = []
    seen_links = set()

    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, search_term in enumerate(search_terms):
        status_text.text(f'Searching: "{search_term}"...')
        progress_bar.progress((i + 1) / len(search_terms))

        try:
            results = google_news.get_news(search_term)
            for entry in results:
                # Convert gnews format to match your existing code
                if entry['url'] not in seen_links:
                    converted_entry = {
                        'title': entry['title'],
                        'link': entry['url'],
                        'source': {'title': entry['publisher']['title']},
                        'published': entry['published date']
                    }
                    all_entries.append(converted_entry)
                    seen_links.add(entry['url'])
        except Exception as e:
            st.warning(f"Error searching for '{search_term}': {e}")

    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()

    # Process and filter results
    filtered_results = []
    seen_titles = set()

    for entry in all_entries:
        title = entry['title']
        link = entry['link']
        media = entry['source']['title']

        # Apply filters
        if exclude_gov and '.gov' in media:
            continue
        if exclude_quiver and 'Quiver Quantitative' in media:
            continue

        # Clean the title
        clean_title = title.replace(f" - {media}", "")
        safe_title = clean_text(clean_title)
        safe_media = clean_text(media)

        if safe_title in seen_titles:
            continue

        seen_titles.add(safe_title)

        # Check if it's a Kansas outlet
        is_kansas = any(kansas_outlet in media for kansas_outlet in kansas_outlets)

        filtered_results.append({
            'title': safe_title,
            'media': safe_media,
            'link': link,
            'is_kansas': is_kansas,
            'published': entry['published']
        })

    return filtered_results, len(all_entries)

# Main search button
if st.sidebar.button("🔍 Search Jerry Moran News", type="primary"):
    with st.spinner('Searching across multiple terms...'):
        results, total_found = search_jerry_moran_news(days, exclude_gov, exclude_quiver)

    if results:
        st.success(f"Found {len(results)} unique articles (from {total_found} total results)")

        # Summary statistics
        kansas_count = sum(1 for r in results if r['is_kansas'])
        if kansas_count > 0:
            st.info(f"📍 {kansas_count} articles from Kansas outlets")

        # Display results
        st.markdown("---")

        for i, article in enumerate(results, 1):
            kansas_indicator = "*" if article['is_kansas'] else ""

            # Create expandable section for each article
            with st.expander(f"{i}. {kansas_indicator}{article['media']}: {article['title'][:80]}..."):
                st.markdown(f"""
                **Media Source:** {kansas_indicator}{article['media']}
                **Title:** {article['title']}
                **Published:** {article['published']}
                **Link:** [{article['title']}]({article['link']})
                """)

        # Create downloadable content
        markdown_content = "# Jerry Moran News\n\n"
        markdown_content += f"*Search conducted on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        markdown_content += f"*Time range: Last {days} days*\n\n"

        for article in results:
            kansas_indicator = "*" if article['is_kansas'] else ""
            markdown_content += f"- {kansas_indicator}{article['media']}: [{article['title']}]({article['link']})\n"

        # Download buttons
        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="📥 Download as Markdown",
                data=markdown_content,
                file_name=f"jerry_moran_news_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )

        with col2:
            # Create simple text version
            text_content = "Jerry Moran News\n" + "="*50 + "\n\n"
            for article in results:
                kansas_indicator = "*" if article['is_kansas'] else ""
                text_content += f"{kansas_indicator}{article['media']}: {article['title']}\n{article['link']}\n\n"

            st.download_button(
                label="📄 Download as Text",
                data=text_content,
                file_name=f"jerry_moran_news_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )

    else:
        st.warning("No articles found. Try adjusting your search parameters.")

# Information in sidebar
st.sidebar.markdown("---")
st.sidebar.info("""
**Search Terms Used:**
- Jerry Moran
- Senator Jerry Moran
- Senator Moran
- Sen. Moran
- Sen. Jerry Moran
- Sens. Moran
- Sens. Jerry Moran
""")

st.sidebar.markdown("---")
st.sidebar.info("* = Kansas news outlet")

st.sidebar.markdown("---")
st.sidebar.markdown("Built with Streamlit & GNews")

# Show instructions if no search has been run yet
if 'button' not in st.session_state:
    st.markdown("""
    ## How to Use

    1. **Select time range** in the sidebar (1-30 days)
    2. **Choose filters** to exclude government sources or Quiver Quantitative
    3. **Click "Search"** to find Jerry Moran news across multiple search variations
    4. **View results** with Kansas outlets marked with * before the media name
    5. **Download** results as Markdown or Text files

    The app searches multiple variations of Jerry Moran's name to ensure comprehensive coverage.

    **Kansas outlets will be highlighted with * including:**
    - Kansas Reflector
    - The Topeka Capital-Journal
    - The Wichita Eagle
    - KCLY Radio, KWCH, KSN-TV
    - Kansas City Star
    - And many more local Kansas news sources
    """)
