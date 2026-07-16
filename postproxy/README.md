# PostProxy Skill

An Agent Skill for managing social media posts across multiple platforms using the [PostProxy API](https://postproxy.dev/).

## Overview

This skill enables AI agents to create, manage, and schedule social media posts across Facebook, Instagram, TikTok, LinkedIn, YouTube, X/Twitter, and Threads through the PostProxy API.

## Installation

Install this skill using the `skills` CLI:

```bash
npx skills add postproxy/postproxy-skill
```

Or install to specific agents:

```bash
npx skills add postproxy/postproxy-skill -a cursor -a claude-code
```

## Setup

Before using this skill, you need to:

1. Get your PostProxy API key from [https://app.postproxy.dev/api_keys](https://app.postproxy.dev/api_keys)
2. Set it as an environment variable:

```bash
export POSTPROXY_API_KEY=your_api_key_here
```

## Usage Examples

Once installed, your AI agent can use this skill to:

### Create a post across multiple platforms

```
Create a post saying "Check out our new feature!" and publish it to Twitter, LinkedIn, and Threads
```

### Schedule a post

```
Schedule a post for tomorrow at 9 AM saying "Good morning! Here's today's update" to Twitter
```

### Create a draft with media

```
Create a draft post with the image from ./screenshot.png and the text "New product launch" for Instagram
```

### List and manage posts

```
Show me all my scheduled posts
```

```
Delete the post with ID 12345
```

## Supported Platforms

- Facebook
- Instagram
- TikTok
- LinkedIn
- YouTube
- X/Twitter
- Threads

## Features

- ✅ Create posts with text and media
- ✅ Schedule posts for future publication
- ✅ Create drafts for review before publishing
- ✅ Upload local files as media attachments
- ✅ Publish drafts when ready
- ✅ Delete posts
- ✅ List profiles and posts
- ✅ Platform-specific parameters (Instagram Reels, YouTube titles, etc.)

## API Documentation

For detailed API documentation, visit [https://postproxy.dev/](https://postproxy.dev/)

## Requirements

- PostProxy API key (get one at [https://app.postproxy.dev/api_keys](https://app.postproxy.dev/api_keys))
- Environment variable `POSTPROXY_API_KEY` must be set

## License

See the repository for license information.

## Related Links

- [PostProxy Website](https://postproxy.dev/)
- [PostProxy API Documentation](https://postproxy.dev/)
- [Skills.sh Directory](https://skills.sh/)
