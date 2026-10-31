import helper
import sys 
url = False
minutes = input("Split interval in minutes: ")


if len(sys.argv) > 1:
    url = sys.argv[1]

if url:
    helper.download(url, minutes) 
else:
    listed = helper.scan_videos()
    for url in listed:
        helper.download(url, minutes) 

#else:
#    listed = helper.scan()
#    for _scan in listed:
#        listening = helper.DIR__ / helper.Path(_scan.name) / "Listening.md"
#
#        if listening.exists():
#            content = listening.read_text(encoding="utf-8")
#
#            urls = helper.re.findall(
#                r'https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[^\s)]+',
#                content
#            )
#
#            for url in urls:
#                helper.download(url, minutes)

