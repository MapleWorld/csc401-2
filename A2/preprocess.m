function outSentence = preprocess( inSentence, language )
%
%  preprocess
%
%  This function preprocesses the input text according to language-specific rules.
%  Specifically, we separate contractions according to the source language, convert
%  all tokens to lower-case, and separate end-of-sentence punctuation 
%
%  INPUTS:
%       inSentence     : (string) the original sentence to be processed 
%                                 (e.g., a line from the Hansard)
%       language       : (string) either 'e' (English) or 'f' (French) 
%                                 according to the language of inSentence
%
%  OUTPUT:
%       outSentence    : (string) the modified sentence
%
%  Template (c) 2011 Frank Rudzicz 

  global CSC401_A2_DEFNS
  
  % first, convert the input sentence to lower-case and add sentence marks 
  inSentence = [CSC401_A2_DEFNS.SENTSTART ' ' lower( inSentence ) ' ' CSC401_A2_DEFNS.SENTEND];

  % trim whitespaces down 
  inSentence = regexprep( inSentence, '\s+', ' '); 

  % initialize outSentence
  outSentence = inSentence;

  % perform language-agnostic changes
  % TODO: your code here
  %    e.g., outSentence = regexprep( outSentence, 'TODO', 'TODO');
  
  % Separate sentence final punctuation
  outSentence = regexprep(outSentence, '(.*?)([\?!\.]+) (SENTEND)', '$1 $2 $3');
  % Separate other stuff
  outSentence = regexprep(outSentence, '(.*?)([,;:\(\)\+-<>="])(.*?)', '$1 $2 $3');
  % Separate dashes between parentheses
  outSentence = regexprep(outSentence, '(.*?\(.*?)(-)(.*?\).*?)', '$1 $2 $3');
  
  switch language
   case 'e'
    % Simple heuristic for apostrophes:
    % - If last character, split on its own
    % - If its the second last and last is 's', take those 2
    % - If its the first character, leave it there
    % - If it's third last and ending is "'ll", take that
    % - Otherwise take 1 character before it to end
    outSentence = regexprep(outSentence, '(.*?[^ ])('')( .*?)', '$1 $2$3');
    outSentence = regexprep(outSentence, '(.*?[^ ])(''s)( .*?)', '$1 $2$3');
    outSentence = regexprep(outSentence, '(.*?[^ ])(''ll)( .*?)', '$1 $2$3');
    outSentence = regexprep(outSentence, '(.*?[^ ])(.''.*)( .*?)', '$1 $2$3');

   case 'f'
    outSentence = regexprep(outSentence, '(.*? )([cdjlmnst]'')([^ ].*?)', '$1$2 $3');
    outSentence = regexprep(outSentence, '(.*? )(d'') (abord|accord|ailleurs||habitude)( .*?)', '$1$2$3$4');
    outSentence = regexprep(outSentence, '(.*? )(qu'')([^ ].*?)', '$1$2 $3');
    outSentence = regexprep(outSentence, '(.*? )(lorsqu'')(on|il) ', '$1$2 $3');
    outSentence = regexprep(outSentence, '(.*? )(puisqu'')(on|il) ', '$1$2 $3');
    

  end

  % trim extra whitespace again as we may have added excess spaces
  outSentence = regexprep( outSentence, '\s+', ' '); 
  % change unpleasant characters to codes that can be keys in dictionaries
  outSentence = convertSymbols( outSentence );

