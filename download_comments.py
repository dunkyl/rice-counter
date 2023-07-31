import sys, asyncio, os
import csv
from SlyYTDAPI import *

if not os.path.exists('api_key.txt'):
    open('api_key.txt', mode='w')
    print("Put your API key in api_key.txt")
    exit(-1)

async def main(video_id):
    yt = YouTubeData(open('api_key.txt').read().strip())

    my_video = await yt.video(video_id)
    print(F"Downloading comments for: {my_video.title}")

    print("0 comments collected...     ", end='')
    all_comments = []
    async for comment in my_video.comments(limit=None):
        all_comments.append(comment)
        if len(all_comments) % 10 == 0:
            print(F"\r{len(all_comments)} comments collected...     ", end='')

    print(F"\r{len(all_comments)} comments collected!       ")

    all_comments_flat: list[tuple[Comment, bool]] = []
    for c in all_comments:
        all_comments_flat.extend([(c, False), *((r, True) for r in (c.replies or []))])

    print(F" ⬑  that's {len(all_comments_flat)} counting replies")

    all_channel_ids = [c.author_channel_id for c, _ in all_comments_flat]

    print("getting commenter info...")
    all_commenters = await yt.channels(all_channel_ids, Part.SNIPPET)
    print(F"{len(all_commenters)} unique commenters!")

    commenters_by_id = { c.id: c for c in all_commenters }

    output = open(F'comments_{my_video.id}.csv', "w", encoding='utf8', newline='')
    writer = csv.writer(output)

    writer.writerow([ "Timestamp", 
                      "Display Name",
                      "Channel @",
                      "Channel ID",
                      "Comment",
                      "Is Reply?" ])

    for comment, is_reply in all_comments_flat:
        is_reply = "TRUE" if is_reply else "FALSE"
        commenter = commenters_by_id[comment.author_channel_id]
        writer.writerow([
            comment.created_at.isoformat('T'),
            comment.author_display_name,
            commenter.at_username,
            comment.author_channel_id,
            comment.body,
            is_reply
        ])

    print(F'Data written to comments_{my_video.id}.csv')

match sys.argv:
    case [_, video_id]:
        asyncio.run(main(video_id))
    case _:
        print(
        "Usage:"
        "    py download_comments.py <VIDEO_ID>" )