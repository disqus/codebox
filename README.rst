Linkinus Support
----------------

Save this as <command>.scpt in your scripts folder::

    -- --------------------------------------
    -- Private Paste Script for Linkinus
    -- by David Cramer
    -- Version 1.0
    -- --------------------------------------

    on linkinuscmd(paste_type)
    	set theURL to ""
    	set orgSlug to "YOUR ORG SLUG"
    	set apiToken to "YOUR API TOKEN"
    	set baseURL to "http://codebox.cc/" & orgSlug & "/new"

    	do shell script "pbpaste | curl " & baseURL & " -X POST -F \"lang=" & paste_type & "\" -F \"text=<-\" -F \"api_token=" & apiToken & "\" -s -L -o /dev/null -w \"%{url_effective}\""
    	set theURL to result
	
    	if theURL is not "" and theURL is not baseURL then
    		return theURL
    	end if
    end linkinuscmd

    linkinuscmd()