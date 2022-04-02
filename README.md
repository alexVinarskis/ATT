# ATT - Android Translate Tools

A set of python tools for simplyfying translation of Android projects. Insiparation was taken from  <a href="https://github.com/Ra-Na/GTranslate-strings-xml" title="GTranslate">this</a> idea, which I have greately <a href="https://github.com/alexVinarskis/GTranslate-strings-xml" title="AWSTranslate">improved</a>.  This repo aims to provide a more complete set of useful utils. All of these are based on AWS translate, and will require installed and configured AWS CLI on your machine. 

## Tools List
1. `strings_add.py` - translates given `values-XX/strings.xml` to new langueges, automatically writes them to dedicated `values-XX` folders. Best way to add new language [coming soon]
2. `strings.py` - 'syncs' translations between existing languages. Eg. when `values` got a new string, this will translate and add the new string to each of existing languages `values-XX`. This does not override any existing strings. Preferable over `strings_add.py`, as it preserves existing strings of existing translations, and only adds missing ones. 
3. `GPP.py` - translation functionalities for Gradle Publish Plugin: listings, release notes [coming soon]
## Features:
`strings_add.py` and `strings.py`:
1. Automatically extract text from strings.xml and reassemble it back for new languages
2. Ignores `translatable=false` strings
3. Preserves HTML atributes (eg. `<i>` etc)
4. Performs structure reconstruction after translation (eg. `\ n` back to `\n` etc) in order to protect HTML atributes 
5. Performs apostrophe reconstruction after translation (`'` to `\'`) in order to prevent android file errors for langs like `it`, `fr` etc.
6. Works both with `string` and `string-array`
7. Ability to choose non default source language

`strings_add.py` only:
1. Supports adding multiple langs at once, space separated
2. Automatically forms values-XX folders for each of the langs


