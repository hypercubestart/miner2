import numpy,datetime,pandas,sys
from pkg_resources import Requirement, resource_filename
from collections import Counter

def correctBatchEffects(df): 
    zscoredExpression = zscore(df)
    means = []
    stds = []
    for i in range(zscoredExpression.shape[1]):
        mean = numpy.mean(zscoredExpression.iloc[:,i])
        std = numpy.std(zscoredExpression.iloc[:,i])
        means.append(mean)
        stds.append(std)
    if numpy.std(means) >= 0.15:
        zscoredExpression = preProcessTPM(df)
    return zscoredExpression

def identifierConversion(expressionData, conversion_table_path=None):

    # if not specified, read conversion table from package data
    if conversion_table_path is None:
        conversion_table_path = resource_filename(Requirement.parse("miner2"),
                                                  'miner2/data/identifier_mappings.txt')

    idMap = pandas.read_csv(conversion_table_path, sep='\t')

    genetypes = list(set(idMap.iloc[:,2]))
    previousIndex = numpy.array(expressionData.index).astype(str)    
    previousColumns = numpy.array(expressionData.columns).astype(str)  
    bestMatch = []
    for geneType in genetypes:
        subset = idMap[idMap.iloc[:,2]==geneType]
        subset.index = subset.iloc[:,1]
        mappedGenes = list(set(previousIndex)&set(subset.index))
        mappedSamples = list(set(previousColumns)&set(subset.index))
        if len(mappedGenes)>=max(10,0.01*expressionData.shape[0]):
            if len(mappedGenes)>len(bestMatch):
                bestMatch = mappedGenes
                state = "original"
                gtype = geneType
                continue
        if len(mappedSamples)>=max(10,0.01*expressionData.shape[1]):
            if len(mappedSamples)>len(bestMatch):
                bestMatch = mappedSamples
                state = "transpose"
                gtype = geneType
                continue

    mappedGenes = bestMatch
    mappedGenes.sort() # ALO this new line in miner2 is surprisingly important for reproducibility. Otherwise expressionData varies in last digits of floats and every thing down the road changes slightly
    subset = idMap[idMap.iloc[:,2]==gtype] 
    subset.index = subset.iloc[:,1]

    if len(bestMatch) == 0:
        print("Error: Gene identifiers not recognized")

    if state == "transpose":
        expressionData = expressionData.T

    try:
        convertedData = expressionData.loc[mappedGenes,:]
    except:
        convertedData = expressionData.loc[numpy.array(mappedGenes).astype(int),:]

    conversionTable = subset.loc[mappedGenes,:]
    conversionTable.index = conversionTable.iloc[:,0]
    conversionTable = conversionTable.iloc[:,1]
    conversionTable.columns = ["Name"]

    newIndex = list(subset.loc[mappedGenes,"Preferred_Name"])
    convertedData.index = newIndex

    duplicates = [item for item, count in Counter(newIndex).items() if count > 1]
    singles = list(set(convertedData.index)-set(duplicates))

    ### ALO these two sorting does not seem to compromise reproducibility
    #duplicates.sort()
    #singles.sort()

    corrections = []

    for duplicate in duplicates:
        dupData = convertedData.loc[duplicate,:]
        firstChoice = pandas.DataFrame(dupData.iloc[0,:]).T
        corrections.append(firstChoice)

    if len(corrections) > 0:
        #print('there are corrections')
        correctionsDf = pandas.concat(corrections,axis=0)
        uncorrectedData = convertedData.loc[singles,:]
        #print('\t before concat',numpy.mean(convertedData.iloc[:,0]))
        convertedData = pandas.concat([uncorrectedData,correctionsDf],axis=0)
        #print('\t during corrections',numpy.mean(convertedData.iloc[:,0]))

    #print('right after corrections',numpy.mean(convertedData.iloc[:,0]))
    #print()

    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S \t {} out of {} gene names converted to ENSEMBL IDs".format(convertedData.shape[0],expressionData.shape[0])))

    return convertedData, conversionTable

def main(filename, conversion_table_path=None):
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S \t expression data reading"))
    rawExpression = readFileToDf(filename)

    firstPatient = rawExpression.iloc[:,0]
    #print('raw',type(firstPatient),len(firstPatient),numpy.mean(firstPatient))

    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S \t expression data recovered: {} features by {} samples".format(rawExpression.shape[0],rawExpression.shape[1])))
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S \t expression data transformation"))

    rawExpressionZeroFiltered = removeNullRows(rawExpression)
    zscoredExpression = correctBatchEffects(rawExpressionZeroFiltered)

    firstPatient = zscoredExpression.iloc[:,0]
    #print('zscore',type(firstPatient),len(firstPatient),numpy.mean(firstPatient))

    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S \t gene ID conversion"))
    expressionData, conversionTable = identifierConversion(zscoredExpression,
                                                           conversion_table_path)

    firstPatient = expressionData.iloc[:,0]
    #print('expressionData',type(firstPatient),len(firstPatient),numpy.mean(firstPatient))

    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S \t working expression data: {} features by {} samples".format(expressionData.shape[0],expressionData.shape[1])))
    return expressionData, conversionTable

def readFileToDf(filename):
    extension = filename.split(".")[-1]
    if extension == "csv":
        df = pandas.read_csv(filename,index_col=0,header=0)
        shape = df.shape
        if shape[1] == 0:
            df = pandas.read_csv(filename,index_col=0,header=0,sep="\t")
    elif extension == "txt":
        df = pandas.read_csv(filename,index_col=0,header=0,sep="\t")
        shape = df.shape
        if shape[1] == 0:
            df = pandas.read_csv(filename,index_col=0,header=0)    
    return df

def removeNullRows(df):
    minimum = numpy.percentile(df,0)
    if minimum == 0:
        filteredDf = df.loc[df.sum(axis=1)>0,:]
    else:
        filteredDf = df
    return filteredDf

def zscore(expressionData):
    zero = numpy.percentile(expressionData,0)
    meanCheck = numpy.mean(expressionData[expressionData>zero].mean(axis=1,skipna=True))
    if meanCheck<0.1:
        return expressionData
    means = expressionData.mean(axis=1,skipna=True)
    stds = expressionData.std(axis=1,skipna=True)
    try:
        transform = ((expressionData.T - means)/stds).T
    except:
        passIndex = numpy.where(stds>0)[0]
        transform = ((expressionData.iloc[passIndex,:].T - means[passIndex])/stds[passIndex]).T
    print("completed z-transformation.")
    return transform
