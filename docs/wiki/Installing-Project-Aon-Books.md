# Installing Project Aon Books

Lone Wolf Action Assistant Redux does not include the Project Aon book files.

Download the books from Project Aon for personal use, then extract the standard HTML files into the local `books\lw` folder. The app will read them from your machine; we do not bundle or upload them.

## Book 1

Book 1 should live here:

```text
books\lw\01fftd
```

The folder should contain files like:

```text
sect1.htm
sect2.htm
sect350.htm
```

## Local Install Page

When the app is running, open:

```text
http://127.0.0.1:8797/install-books.html
```

That page checks which local books are installed and shows the expected folders.

## Do Not Commit Books

The `books` folder is for your local personal copies only.

Do not commit it. Do not package it. Do not upload it to a release.

## Future Books

Book 2 and later will use the same shape:

```text
books\lw\<bookcode>
```

Run the book pipeline before claiming assistant support for a new book. Each book can add new rules, starting gear choices, carry-over checks, and route automation.
