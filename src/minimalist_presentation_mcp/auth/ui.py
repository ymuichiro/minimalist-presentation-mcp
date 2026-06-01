from __future__ import annotations

from html import escape
from urllib.parse import quote

from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response

from minimalist_presentation_mcp.auth.oauth import InAppOAuthProvider
from minimalist_presentation_mcp.auth.store import AuthStore
from minimalist_presentation_mcp.storage.deck_store import DeckStore

MESSAGES = {
    "ja": {
        "app": "Zen Presentation",
        "login": "ログイン",
        "username": "ユーザー名",
        "password": "パスワード",
        "dashboard": "ダッシュボード",
        "mypage": "マイページ",
        "logout": "ログアウト",
        "decks": "作成した資料",
        "no_decks": "作成した資料はまだありません。",
        "settings": "表示設定",
        "language": "言語",
        "theme": "テーマ",
        "light": "ライト",
        "dark": "ダーク",
        "save": "保存",
        "invalid_login": "ユーザー名またはパスワードが正しくありません。",
    },
    "en": {
        "app": "Zen Presentation",
        "login": "Log in",
        "username": "Username",
        "password": "Password",
        "dashboard": "Dashboard",
        "mypage": "My Page",
        "logout": "Log out",
        "decks": "My decks",
        "no_decks": "No decks have been created yet.",
        "settings": "Display settings",
        "language": "Language",
        "theme": "Theme",
        "light": "Light",
        "dark": "Dark",
        "save": "Save",
        "invalid_login": "Invalid username or password.",
    },
}


def user_language(user: dict | None) -> str:
    return (user or {}).get("language") if (user or {}).get("language") in MESSAGES else "ja"


def user_theme(user: dict | None) -> str:
    return (user or {}).get("theme") if (user or {}).get("theme") in {"light", "dark"} else "light"


def t(user: dict | None, key: str) -> str:
    return MESSAGES[user_language(user)][key]


def page(title: str, body: str, *, user: dict | None = None) -> HTMLResponse:
    theme = user_theme(user)
    nav = ""
    if user:
        nav = f"""
        <nav>
          <a href="/dashboard">{escape(t(user, "dashboard"))}</a>
          <a href="/mypage">{escape(t(user, "mypage"))}</a>
          <form method="post" action="/logout"><button>{escape(t(user, "logout"))}</button></form>
        </nav>
        """
    return HTMLResponse(
        f"""<!doctype html>
<html lang="{escape(user_language(user))}" data-theme="{escape(theme)}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{ --bg: #f7f5ef; --panel: #fff; --ink: #171717; --muted: #666; --line: #ddd; --accent: #8f2f2b; }}
    [data-theme="dark"] {{ --bg: #111; --panel: #1c1c1c; --ink: #f3f3f3; --muted: #aaa; --line: #383838; --accent: #e08b80; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: var(--bg); color: var(--ink); }}
    header {{ display: flex; align-items: center; justify-content: space-between; padding: 16px 24px; border-bottom: 1px solid var(--line); background: var(--panel); }}
    main {{ width: min(920px, calc(100vw - 32px)); margin: 32px auto; }}
    nav {{ display: flex; align-items: center; gap: 14px; }}
    a {{ color: var(--accent); text-decoration: none; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 24px; }}
    label {{ display: block; color: var(--muted); margin: 14px 0 6px; }}
    input, select {{ width: 100%; padding: 10px 12px; border: 1px solid var(--line); border-radius: 6px; background: var(--panel); color: var(--ink); }}
    button {{ padding: 9px 13px; border-radius: 6px; border: 1px solid var(--line); background: var(--accent); color: white; cursor: pointer; }}
    nav form {{ margin: 0; }}
    nav button {{ background: transparent; color: var(--accent); }}
    .deck-list {{ display: grid; gap: 10px; padding: 0; list-style: none; }}
    .deck-list li {{ border: 1px solid var(--line); border-radius: 8px; padding: 14px; }}
    .error {{ color: #b00020; }}
  </style>
</head>
<body>
  <header><strong>{escape(t(user, "app"))}</strong>{nav}</header>
  <main>{body}</main>
</body>
</html>"""
    )


def get_session_user(request: Request, store: AuthStore) -> dict | None:
    return store.get_browser_session_user(request.cookies.get("mfd_session"))


def redirect_to_login(request: Request) -> RedirectResponse:
    return RedirectResponse(f"/login?next={quote(str(request.url.path))}", status_code=302)


def login_form(request: Request, *, user: dict | None = None, error: str | None = None) -> HTMLResponse:
    auth_request = request.query_params.get("auth_request", "")
    next_path = request.query_params.get("next", "/dashboard")
    body = f"""
    <section class="panel">
      <h1>{escape(t(user, "login"))}</h1>
      {'<p class="error">' + escape(error) + '</p>' if error else ''}
      <form method="post" action="/login">
        <input type="hidden" name="auth_request" value="{escape(auth_request)}">
        <input type="hidden" name="next" value="{escape(next_path)}">
        <label>{escape(t(user, "username"))}</label>
        <input name="username" autocomplete="username" required>
        <label>{escape(t(user, "password"))}</label>
        <input name="password" type="password" autocomplete="current-password" required>
        <p><button>{escape(t(user, "login"))}</button></p>
      </form>
    </section>
    """
    return page(t(user, "login"), body, user=user)


async def handle_login_post(request: Request, store: AuthStore, provider: InAppOAuthProvider) -> Response:
    form = await request.form()
    username = str(form.get("username") or "")
    password = str(form.get("password") or "")
    user = store.authenticate_user(username, password)
    if not user:
        return login_form(request, error=MESSAGES["ja"]["invalid_login"])
    session_id = store.create_browser_session(user["id"])
    auth_request = str(form.get("auth_request") or "")
    if auth_request:
        try:
            redirect_uri, query = provider.complete_authorization(auth_request, user["id"])
        except ValueError:
            return page("Authorization expired", "<section class=\"panel\"><p>Authorization request expired.</p></section>")
        response = RedirectResponse(f"{redirect_uri}{'&' if '?' in redirect_uri else '?'}{query}", status_code=302)
    else:
        next_path = str(form.get("next") or "/dashboard")
        if not next_path.startswith("/"):
            next_path = "/dashboard"
        response = RedirectResponse(next_path, status_code=302)
    secure_cookie = request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https"
    response.set_cookie("mfd_session", session_id, httponly=True, secure=secure_cookie, samesite="lax", path="/")
    return response


def dashboard_page(user: dict, deck_store: DeckStore) -> HTMLResponse:
    decks = deck_store.list_by_owner(user["id"])
    items = "".join(
        f'<li><a href="/decks/{escape(deck["deck_id"])}">{escape(deck["title"])}</a><br><small>{escape(deck["created_at"])}</small></li>'
        for deck in decks
    )
    if not items:
        items = f"<li>{escape(t(user, 'no_decks'))}</li>"
    body = f"""
    <section class="panel">
      <h1>{escape(t(user, "dashboard"))}</h1>
      <h2>{escape(t(user, "decks"))}</h2>
      <ul class="deck-list">{items}</ul>
    </section>
    """
    return page(t(user, "dashboard"), body, user=user)


def mypage(user: dict) -> HTMLResponse:
    language = user_language(user)
    theme = user_theme(user)
    body = f"""
    <section class="panel">
      <h1>{escape(t(user, "mypage"))}</h1>
      <h2>{escape(t(user, "settings"))}</h2>
      <form method="post" action="/mypage/preferences">
        <label>{escape(t(user, "language"))}</label>
        <select name="language">
          <option value="ja" {'selected' if language == 'ja' else ''}>日本語</option>
          <option value="en" {'selected' if language == 'en' else ''}>English</option>
        </select>
        <label>{escape(t(user, "theme"))}</label>
        <select name="theme">
          <option value="light" {'selected' if theme == 'light' else ''}>{escape(t(user, "light"))}</option>
          <option value="dark" {'selected' if theme == 'dark' else ''}>{escape(t(user, "dark"))}</option>
        </select>
        <p><button>{escape(t(user, "save"))}</button></p>
      </form>
    </section>
    """
    return page(t(user, "mypage"), body, user=user)
