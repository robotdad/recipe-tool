# 📄 Product Requirements Document

**Project Title**: Kid-Safe YouTube Browser with Admin Video Whitelist

## 🎯 Purpose

Create a secure, minimal, browser-based interface for children to safely watch only parent-approved YouTube videos, using a curated `videos.json` list and embedded `youtube-nocookie.com` players. A basic admin UI (protected by a simple passcode) will allow the parent to add, edit, or remove video entries.

This project is intended for use in a controlled environment, such as a home or classroom, where parents or guardians can manage the content.

## 📱 Target Platform

- **Web**: Desktop and mobile browsers
- **Framework**: Vanilla JavaScript, HTML, CSS
- **Hosting**: Local or cloud (e.g., GitHub Pages, Netlify)
- **No external libraries**: Pure JavaScript for simplicity and security
- **No backend**: All data is stored in a JSON file (`videos.json`) and managed through the admin UI
- **No database**: All data is stored in a JSON file (`videos.json`) and managed through the admin UI
- **No user accounts**: No login or registration required

## 🧑‍🤝‍🧑 Users

| User Type        | Goals                                                                                                                |
| ---------------- | -------------------------------------------------------------------------------------------------------------------- |
| **Child**        | Tap/search from an approved list of YouTube videos and watch them without exposure to suggestions or external links. |
| **Parent/Admin** | Log in via passcode to manage the approved video list through a simple UI that edits `videos.json`.                  |

## 🧩 Key Features

### Viewer Mode (Default)

- ✅ Search box with dropdown/autocomplete
- ✅ If no search term, show all videos in a list
- ✅ Click or keyboard-select a video from list
- ✅ Video loads in a `youtube-nocookie.com` iframe
- ✅ Autoplay next video after one ends
- ✅ Thumbnail previews in suggestions
- ✅ No video selected by default
- ✅ Optional back-to-start looping

### Admin Mode (Triggered by Passcode)

- ✅ Simple passcode-based login (e.g. `/admin?code=XYZ123`)
- ✅ Display current `videos.json` entries as editable rows
- ✅ Add new video entry (title + YouTube ID)
- ✅ Remove entries
- ✅ Save changes (overwrites `videos.json`)
- ✅ Default passcode configurable in code (e.g. `defaultAdminPass = "kidwatch"`)

## 🔒 Security / Safety

- ❌ No access to `youtube.com` domain (only `youtube-nocookie.com`)
- ❌ No autoplay suggestions or external links
- ❌ No browsing/search beyond what's in `videos.json`
- ✅ Fully whitelisted domain support for Family Link / DNS tools
- ⚠️ Admin UI is not intended for multi-user environments—local or limited use only

## ⚙️ Config / Constants

| Setting         | Description                            |
| --------------- | -------------------------------------- |
| `adminPasscode` | Default value used to enter admin mode |
| `loopVideos`    | Whether to loop to first video at end  |

## Initial videos.json content

IMPORTANT: Include this in the spec as the initial `videos.json` file to ensure the app has something to display.

```json
[
  {
    "title": "Why Do Cats Miaow? | Cats Uncovered | BBC",
    "videoId": "qeUM1WDoOGY"
  },
  {
    "title": "Fascinating Colours of the Animal Kingdom | BBC Earth",
    "videoId": "Eo-ymUtJ2NM"
  },
  {
    "title": "Edward the Peacock is on the Loose! | Sam's Zookeeper Challenge",
    "videoId": "7MFBWmDDZoU"
  }
]
```

## 🧪 Edge Cases

- If video fails to load, try next in list or show error
- Block re-entry to admin without correct passcode
- Admin edits must validate input (no blank titles, malformed IDs)

## 🧱 Future Enhancements

- Tag/categorize videos ("Science", "Music", "Stories")
- Import multiple video URLs at once
- Offline/local mode fallback
- Admin email/password login (if hosted backend exists)
