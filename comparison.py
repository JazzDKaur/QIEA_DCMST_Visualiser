"""Static, user-supplied reported costs; independent of loaded solution files."""
import io
import pandas as pd
import streamlit as st

DATA = '''Instance,Vertex,D,Ernst,HES-EA,ABA,HSSGA,AD-QIEA-2ES Final
CRD300,30,2,4472,-,-,-,3809
CRD300,30,3,3634,-,-,-,3624
CRD300,30,4,3634,-,-,-,3624
CRD300,30,5,3634,-,-,-,3624
CRD500,50,2,5312,-,-,-,5288
CRD500,50,3,4931,-,-,-,4910
CRD500,50,4,4931,-,-,-,4910
CRD500,50,5,4931,-,-,-,4910
CRD501,50,2,5625,5553,5706,5553,5535
CRD501,50,3,5126,5126,5126,5126,5111
CRD501,50,4,5126,-,-,-,5111
CRD501,50,5,5126,-,-,-,5111
CRD502,50,2,5507,5480,5663,5480,5462
CRD502,50,3,4898,-,-,-,4877
CRD502,50,4,4898,-,-,-,4877
CRD502,50,5,4898,-,-,-,4877
SHRD159,15,2,906,904,904,904,904
SHRD159,15,3,597,597,597,597,597
SHRD159,15,4,430,430,430,430,430
SHRD159,15,5,332,332,332,332,334
SHRD200,20,2,1873,1679,1679,1679,1679
SHRD200,20,3,1100,1088,1088,1088,1088
SHRD200,20,4,829,802,802,802,804
SHRD200,20,5,638,627,627,627,627
SHRD300,30,2,4560,3992,3992,3992,3992
SHRD300,30,3,2738,2592,2592,2592,2592
SHRD300,30,4,1965,1905,1905,1905,1905
SHRD300,30,5,1526,1504,1504,1504,1504
STR300,30,2,4173,-,-,-,4173
STR300,30,3,3924,-,-,-,3924
STR300,30,4,3671,-,-,-,3761
STR300,30,5,3605,-,-,-,3605
STR500,50,2,4471,-,-,-,4420
STR500,50,3,4128,-,-,-,4118
STR500,50,4,3962,-,-,-,3956
STR500,50,5,3807,-,-,-,3807
SYM300,30,2,1376,-,-,-,1376
SYM300,30,3,1012,-,-,-,1012
SYM300,30,4,965,-,-,-,965
SYM300,30,5,959,-,-,-,959
SYM500,50,2,2522,1759,1759,1759,1759
SYM500,50,3,1156,1156,1156,1156,1156
SYM500,50,4,1105,1105,1105,1105,1105
SYM500,50,5,1098,1098,1098,1098,1098
'''

PARAGRAPH = '''In addition to the controlled comparison among B-QIEA, AD-QIEA, and AD-QIEA-2ES, the solution quality of the complete framework was also assessed against the Ernst reference values [1] and published results for HES-EA [2], ABA [3], and HSSGA [4]. This external comparison includes 44 instance-degree combinations for the Ernst reference and 19 overlapping combinations for each competing algorithm. Section 5.3 presents the comparison of reported solution costs and the corresponding relative-gap analysis to quantify deviations from the specified reference values.'''

REFERENCES = '''[1] Ernst, A.T., n.d. Degree constrained minimum spanning tree dataset. Operations Research Benchmark Datasets. Available at: https://andreas-ernst.github.io/Mathprog-ORlib/info/readmeDCMST.html (accessed 10 October 2026).

[2] Raidl, G.R., Julstrom, B.A., 2003. Edge-sets: An effective evolutionary coding of spanning trees. IEEE Transactions on Evolutionary Computation 7 (3), 225–239. https://doi.org/10.1109/TEVC.2002.807275

[3] Bui, T.N., Zrncic, C.M., 2006. An ant-based algorithm for finding degree-constrained minimum spanning tree. In: Proceedings of the 8th Annual Conference on Genetic and Evolutionary Computation (GECCO ’06), pp. 11–18. Association for Computing Machinery, New York, NY, USA. https://doi.org/10.1145/1143997.1144000

[4] Singh, K., Sundar, S., 2020. A hybrid genetic algorithm for the degree-constrained minimum spanning tree problem. Soft Computing 24 (3), 2169–2186. https://doi.org/10.1007/s00500-019-04051-x'''


def comparison_data():
    return pd.read_csv(io.StringIO(DATA), dtype=str, keep_default_na=False)


def render_comparison():
    st.subheader('Reported solution costs')
    st.write(PARAGRAPH)
    st.caption('Static values supplied for this comparison. “-” denotes an unavailable reported result. This table does not update from the selected solution workbook.')
    st.dataframe(comparison_data(), hide_index=True, width='stretch', height=620)
    st.download_button('Download comparison table (CSV)', DATA.encode('utf-8'),file_name='DCMST_reported_costs.csv',mime='text/csv')
    st.subheader('References')
    st.markdown(REFERENCES)
