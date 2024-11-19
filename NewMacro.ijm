open("D:/projects/ImageAnalysis/AnalyzeImage/static/uploads/arx_NaCl_NaCl_0126_090523_1_100perc_10uL_21C_40RH_20800um.jpg");
run("Set Measurements...", "area mean standard modal min centroid center perimeter bounding fit shape feret's integrated median skewness kurtosis area_fraction stack redirect=None decimal=3");
run("Measure");
saveAs("Results", "D:/projects/ImageAnalysis/AnalyzeImage/ImageJResults.csv");
close;
run("Quit");
