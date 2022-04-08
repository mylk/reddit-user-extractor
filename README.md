## reddit-user-extractor

This aspires to be home to a couple OSINT tools about Reddit users.

### comments.py

Extract the comments of a Reddit user.

Example:

```
comments.py -u spez
```

Executing this will produce a CSV file in the current directory.

The CSV file uses `~#~` as a delimiter. Had to be really unique, comments are free text!.  
If you plan to open the file in `LibreOffice`, make sure to set the delimter and check the `Merge delimiters` option.

There is a header line but let me note the extracted fields:

- comment_id
- post_id
- post_title
- subreddit
- date_created
- body

Other command options:

```
-u, --usernames      set the username(s) to extract their comments (required)
-s, --sub-filter     filter user's comments to specific sub (optional)
-p, --page-limit     number of pages to extract (optional)
                     it's 25 comments/page, so setting this to 1 will extact the last 25 comments
-d, --dump           dump to standard output, not to a CSV file. (optional)
-h, --help           show the help message and exit
```

