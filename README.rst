Linkinus Support
----------------

Save this as <command>.scpt in your scripts folder::

    -- --------------------------------------
    -- Private Paste Script for Linkinus
    -- by David Cramer
    -- Version 1.0
    -- --------------------------------------

    on linkinuscmd(paste_type)
    	set isRecognized to true
    	set theURL to ""
    	set orgSlug to "YOUR ORG SLUG"
    	set apiToken to "YOUR API TOKEN"
    	set baseURL to "http://codebox.cc/" & orgSlug & "/new"
    	set highlight_list to {"c++", "css", "diff", "html_rails", "html", "java", "javascript", "objective-c++", "php", "plaintext", "python", "ruby", "sql", "shell-unix-generic"}
	
    	if paste_type is not in highlight_list then
    		set paste_type to "text"
    		set isRecognized to false
    	end if
    	do shell script "pbpaste | curl " & baseURL & " -X POST -F \"lang=" & paste_type & "\" -F \"text=<-\" -F \"api_token=" & apiToken & "\" -s -L -o /dev/null -w \"%{url_effective}\""
    	set theURL to result
	
    	if theURL is not "" and theURL is not baseURL then
    		return theURL
    	end if
    end linkinuscmd

    linkinuscmd()