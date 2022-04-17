## reddit-user-extractor

This aspires to be home to a couple OSINT tools about Reddit users.

The commands produce CSV files in the current directory.

The CSV file uses `~#~` as the delimiter. Don't hate me! It had to be really unique, comments and posts are free text!.  
If you plan to open the file in `LibreOffice`, make sure to set the delimiter and check the `Merge delimiters` option.

### comments.py

Extract the comments of a Reddit user.

Example:

```
comments.py -u spez
```

There is a header line in the CSV file, but let me note the extracted fields:

- comment_id
- post_id
- post_title
- subreddit
- date_created
- body

### posts.py

Extract the posts of a Reddit user.

Example:

```
posts.py -u spez
```

There is a header line in the CSV file, but you can take a glimpse here too:

- id
- title
- subreddit
- flair
- date_created
- url
- body

### Command options

Both commands accept the following options:

```
-u, --usernames        the user(s) to extract the data.
                       separate with commas for multiple values.
-f, --usernames-file   a file that contains the user(s) to extract the data.
                       each value has to be in a new line.
-s, --sub-filter       filter user's data to specific subreddit (optional).
-p, --page-limit       number of pages to examine (optional).
                       for comments, it's 25 comments per page, so setting this to 1 will extact the last 25 comments.
                       for posts, it will look-up the first X pages of data for posts.
-d, --dump             dump to standard output (optional).
-h, --help             show the help message and exit.
```

