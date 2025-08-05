import requests
from bs4 import BeautifulSoup
from mcp.server.fastmcp import Context, FastMCP

SEARCH_ENDPOINT = 'https://www.2025.ieeeigarss.org/search.php'

mcp = FastMCP(name="IGARSS Search Server")

def scrape_sessions(keyword: str='', author: str='') -> list[dict]:
    """
    Parse the IGARSS search results HTML and extract session info.
    """
    # Session cookies and headers
    cookies = {
        '_ga': 'GA1.1.861705804.1743056437',
        '_ga_MGXEB92M25': 'GS1.1.1743500163.2.0.1743500163.0.0.0',
        'PHPSESSID': 'blg6rgs14htmdftk14kv3mp87k'
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8,en-AU;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.2025.ieeeigarss.org',
        'Referer': 'https://www.2025.ieeeigarss.org/search.php',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
        'dnt': '1',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-gpc': '1'
    }

    # Form data simulating radar search
    payload = {
        'SearchField': 'Search',
        'show': 'search',
        'TempDate': '<%=Date%>',
        'ContactEmail': '<%=DecodeString(strAuthorEmail)%>',
        'PaperNum': '',
        'AuthorName': author,
        'authorand': 'and',
        'PaperTitle': keyword,
        'titleand': 'and',
        'topic': '',
        'PrintTime': ''
    }

    # Perform the POST request
    response = requests.post(f'{SEARCH_ENDPOINT}?show=search',
                            headers=headers, cookies=cookies, data=payload)

    soup = BeautifulSoup(response.text, 'html.parser')

    sessions = []

    all_paper_th = soup.findAll('th', string='Paper')
    for paper_th in all_paper_th:
        paper_td = paper_th.find_next_sibling('td')
        paper_link = paper_td.find('a')
        if paper_link:
            paper_title = paper_link.get_text(strip=True)
            sessions.append({"title": paper_title})

    # Locate the <td> next to the <th> with text "Presentation Time"
    index = 0
    all_time_th = soup.findAll('th', string='Presentation Time')
    for time_th in all_time_th:
        time_td = time_th.find_next_sibling('td')
        presentation_time = time_td.get_text(strip=True)
        sessions[index]["time"] = presentation_time
        index += 1
    
    return sessions

@mcp.prompt(title="IGARSS Session Search")
def igarss_search_prompt(author : str, keyword : str) -> str:
    """Prompt for IGARSS session search."""
    return f"Please search for IGARSS sessions with author: {author} and keyword: {keyword}."

@mcp.tool()
async def search(author : str, keyword : str, ctx: Context) -> list[dict[str, str]]:
    """Process IGARSS session matching search query."""
    # Different log levels
    await ctx.debug(f"Debug: Processing '{author}, {keyword}'")
    await ctx.info("Info: Starting processing")

    try:
        result = scrape_sessions(author=author, keyword=keyword)
        await ctx.success("Success: Search processed successfully")
    except Exception as e:
        await ctx.error(f"Error: {str(e)}")

    # Notify about resource changes
    await ctx.session.send_resource_list_changed()

    return result

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
