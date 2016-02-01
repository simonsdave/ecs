# Development Environment

## Configuration

So [github](https://github.com) works as desired put the following kind of
commands in ```~/.profile```.

```bash
export VISUAL=vim
export EDITOR="$VISUAL"
git config --global user.email "simonsdave@gmail.com"
git config --global user.name "Dave Simons"
```

So [vim](http://www.vim.org) works correct create ```~/.vimrc``` containing the following.

```
set ruler
set hlsearch
filetype plugin on
set ts=4
set sw=4
set expandtab
set encoding=UTF8
syntax on
au BufNewFile,BufRead *.raml set filetype=raml
au BufNewFile,BufRead *.json set filetype=json
autocmd Filetype shell setlocal expandtab tabstop=4 shiftwidth=4
autocmd Filetype python setlocal expandtab tabstop=4 shiftwidth=4
autocmd FileType raml setlocal expandtab tabstop=2 shiftwidth=2
```
