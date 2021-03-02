from tablextract_melva.utils import *
from tablextract_melva.table_processing import *

def tables(
	url,
	css_filter='table',
	xpath_filter=None,
	request_cache_time=0,
	add_image_text=True,
	add_link_urls=False,
	text_metadata_dict=None,
	normalization='min-max-global',  # min-max-global, min-max-local, standard, softmax
	clustering_features=['style', 'syntax', 'structural', 'semantic'],  # any subset of those
	dimensionality_reduction='off',  # off, pca, feature-agglomeration
	clustering_method='k-means',  # k-means, agglomerative, melva,
	melva_config=MELVA_DEFAULT_CONFIG
):
	res = []
	for table in locate(url, css_filter, xpath_filter, request_cache_time):
		try:
			segmentate(table, add_image_text, add_link_urls, url, normalization, text_metadata_dict)
			if not discriminate(table): continue
			functional_analysis(table, clustering_features, dimensionality_reduction, clustering_method, romulo_config)
			structural_analysis(table)
			interpret(table)
			compute_score(table)
		except:
			log_error()
			table.error = format_exc()
		res.append(table)
	return res

if __name__ == '__main__':
	# tabs = tables('https://en.wikipedia.org/wiki/Albedo', clustering_method='melva')
	tabs = tables('https://en.wikipedia.org/wiki/1933_Ottawa_Rough_Riders_season', clustering_method='melva')
	for tab in tabs:
		print(render_tabular_array(tab.texts))
		print(render_tabular_array(tab.functions))
		print('=' * 80)