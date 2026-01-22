import streamlit as st
import streamlit.components.v1 as components

def autocomplete_search_box(placeholder="Search...", key="search"):
    """
    Create a Google-style autocomplete search box with real-time suggestions.
    Uses components.html but with minimal height and overflow visible.
    """
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}
            
            html, body {{
                background: transparent;
                overflow: visible;
                height: auto;
            }}
            
            .gourmet-autocomplete-wrapper {{
                position: relative;
                width: 100%;
                font-family: 'Poppins', Arial, sans-serif;
            }}
            
            .gourmet-search-input {{
                width: 100%;
                padding: 12px 15px;
                font-size: 16px;
                border: 2px solid #ddd;
                border-radius: 10px;
                outline: none;
                transition: all 0.3s ease;
                background: white;
                color: #333;
            }}
            
            .gourmet-search-input:focus {{
                border-color: #ff6b6b;
                box-shadow: 0 2px 8px rgba(255, 107, 107, 0.2);
            }}
            
            .gourmet-suggestions-container {{
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: white;
                border: 1px solid #ddd;
                border-top: none;
                border-radius: 0 0 10px 10px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                max-height: 280px;
                overflow-y: auto;
                z-index: 99999;
                display: none;
                margin-top: -2px;
            }}
            
            .gourmet-suggestions-container.show {{
                display: block;
            }}
            
            .gourmet-suggestion-item {{
                padding: 12px 15px;
                cursor: pointer;
                display: flex;
                align-items: center;
                border-bottom: 1px solid #f0f0f0;
                transition: background 0.15s ease;
            }}
            
            .gourmet-suggestion-item:last-child {{
                border-bottom: none;
                border-radius: 0 0 10px 10px;
            }}
            
            .gourmet-suggestion-item:hover {{
                background: #f8f9fa;
            }}
            
            .gourmet-suggestion-icon {{
                margin-right: 12px;
                color: #999;
                font-size: 16px;
            }}
            
            .gourmet-suggestion-text {{
                color: #333;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="gourmet-autocomplete-wrapper">
            <input 
                type="text" 
                class="gourmet-search-input" 
                id="gourmetSearchInput"
                placeholder="{placeholder}"
                autocomplete="off"
            />
            <div class="gourmet-suggestions-container" id="gourmetSuggestionsContainer"></div>
        </div>
        
        <script>
            const searchInput = document.getElementById('gourmetSearchInput');
            const suggestionsContainer = document.getElementById('gourmetSuggestionsContainer');
            let debounceTimer;

            // Function to fetch suggestions from Google using JSONP
            function fetchSuggestions(query) {{
                if (query.length < 2) {{
                    hideSuggestions();
                    return;
                }}
                
                // Remove any existing JSONP script
                const oldScript = document.getElementById('googleSuggestJSONP');
                if (oldScript) oldScript.remove();
                
                // Define the callback function that Google will call
                window.googleCallback = function(data) {{
                    if (data && data[1] && data[1].length > 0) {{
                        displaySuggestions(data[1].slice(0, 8));
                    }} else {{
                        hideSuggestions();
                    }}
                }};
                
                // Create a new script tag for JSONP
                const script = document.createElement('script');
                script.id = 'googleSuggestJSONP';
                script.src = 'https://suggestqueries.google.com/complete/search?client=youtube&ds=yt&q=' + encodeURIComponent(query + ' recipe') + '&callback=googleCallback';
                document.body.appendChild(script);
            }}
            
            // Display suggestions
            function displaySuggestions(suggestions) {{
                suggestionsContainer.innerHTML = '';
                
                suggestions.forEach(function(suggestion) {{
                    let text = Array.isArray(suggestion) ? suggestion[0] : suggestion;
                    
                    let cleanSuggestion = text.replace(' recipe', '').trim();
                    cleanSuggestion = cleanSuggestion.split(' ')
                        .map(function(word) {{ return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase(); }})
                        .join(' ');
                    
                    const item = document.createElement('div');
                    item.className = 'gourmet-suggestion-item';
                    item.innerHTML = '<span class="gourmet-suggestion-icon">🔍</span><span class="gourmet-suggestion-text">' + cleanSuggestion + '</span>';
                    
                    item.onclick = function() {{
                        searchInput.value = cleanSuggestion;
                        hideSuggestions();
                        
                        // Navigate with query param
                        const url = new URL(window.parent.location.href);
                        url.searchParams.set('dish', cleanSuggestion);
                        window.parent.location.href = url.href;
                    }};
                    
                    suggestionsContainer.appendChild(item);
                }});
                
                suggestionsContainer.classList.add('show');
            }}
            
            // Hide suggestions
            function hideSuggestions() {{
                suggestionsContainer.classList.remove('show');
                suggestionsContainer.innerHTML = '';
            }}
            
            // Input event
            searchInput.oninput = function(e) {{
                const query = e.target.value.trim();
                
                clearTimeout(debounceTimer);
                
                if (query.length < 2) {{
                    hideSuggestions();
                    return;
                }}
                
                debounceTimer = setTimeout(function() {{
                    fetchSuggestions(query);
                }}, 200);
            }};
            
            // Enter key
            searchInput.onkeypress = function(e) {{
                if (e.key === 'Enter') {{
                    hideSuggestions();
                    
                    const url = new URL(window.parent.location.href);
                    url.searchParams.set('dish', searchInput.value);
                    window.parent.location.href = url.href;
                }}
            }};
            
            // Blur event - sync to URL when clicking away
            searchInput.onblur = function() {{
                const value = searchInput.value.trim();
                if (value) {{
                    const url = new URL(window.parent.location.href);
                    if (url.searchParams.get('dish') !== value) {{
                        url.searchParams.set('dish', value);
                        window.parent.history.replaceState({{}}, '', url.href);
                    }}
                }}
            }};
            
            // Hide suggestions when clicking outside
            document.onclick = function(e) {{
                if (!e.target.closest('.gourmet-autocomplete-wrapper')) {{
                    hideSuggestions();
                }}
            }};
        </script>
    </body>
    </html>
    """
    
    # Use components.html with enough height for dropdown
    components.html(html_code, height=340, scrolling=False)
