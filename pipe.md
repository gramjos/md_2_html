---
tags: [zsh, pipe, pipeline, linux, command_cut, command_column, command_grep, history_substitution_operator, standard_error, redirection,]
---
#####`Demonstrative` pipe example
![[pipeline_example.png]]
$$ \int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi} $$
Inline image ![[pipeline_example.png]] Above is the partial output of the command `$ ls /bin /usr/bin`. These are the binary executables in the file system.
Say, we wanted to remove the white text. 
`$ ls /bin /usr/bin |grep -v '/bin:$'` 
**Aside**, `:` (colon) is a literal colon and is not a meta-character.
The `-v` or `--invert-match` means, everything that does not match the grep string will be printed to standard out. 
```shell
 $ ls /bin /usr/bin |grep -v '/bin:$'
```
> [!CAUTION] Title
> Contents
> more

> [!DANGER] Title
> Contents
> more

Creating a matrix
$$
\begin{array}{rcl}
	2&5&7 \\
	2&5&7 \\
\end{array}
$$

> [!NOTE] Title
> Contents
> more

fi
