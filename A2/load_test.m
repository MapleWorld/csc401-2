function [eng, fre] = load_test(filename)
	eng = {};
	fre = {}; 
	elines = textread(strcat(filename, '.e'), '%s', 'delimiter', '\n');
	flines = textread(strcat(filename, '.f'), '%s', 'delimiter', '\n');

	for i=1:length(elines)
		eng{i} = preprocess(elines{i}, 'e');
		fre{i} = preprocess(flines{i}, 'f');
	end
