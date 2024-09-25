import streamlit as st
import pandas as pd

# Function to load and clean data with explicit dtypes
def load_and_clean_data(file_path):
    # Explicitly define the dtypes of each column to avoid mixed-type issues
    dtype_mapping = {
        'ID': 'float64',  # Convert to int later
        'species': 'str',
        'is_type_strain_header': 'float64',  # Convert to int later
        'designation_header': 'str',
        'strain_number_header': 'str',  # Skip this in output
    }
    
    # Use low_memory=False to suppress warnings
    df = pd.read_csv(file_path, dtype=dtype_mapping, low_memory=False)
    
    # Convert 'ID' and 'is_type_strain_header' to integers
    df['ID'] = df['ID'].fillna(0).astype(int)
    df['is_type_strain_header'] = df['is_type_strain_header'].fillna(0).astype(int)
    
    # Drop the 'strain_number_header' column
    df = df.drop(columns=['strain_number_header'])
    
    return df

# Function to filter based on type strain checkbox
def filter_by_type_strain(df, type_strain_value):
    return df[df['is_type_strain_header'] == type_strain_value]

# Load the datasets
prod_df = load_and_clean_data('metabolites/prod.csv')
util_df = load_and_clean_data('metabolites/util.csv')
anti_df = load_and_clean_data('metabolites/anti.csv')

# Function to count total occurrences of metabolites
def count_metabolites(df):
    metabolite_columns = df.columns[4:]  # Assuming metabolites start from the 5th column
    return df[metabolite_columns].sum()

# Function to compute broad statistics table
def compute_statistics(prod_df, util_df, anti_df):
    stats = []
    
    # Type strain statistics
    type_strain_species_count = len(prod_df[prod_df['is_type_strain_header'] == 1]['species'].unique())
    type_strain_prod = count_metabolites(prod_df[prod_df['is_type_strain_header'] == 1]).sum()
    type_strain_util = count_metabolites(util_df[prod_df['is_type_strain_header'] == 1]).sum()
    type_strain_anti = count_metabolites(anti_df[prod_df['is_type_strain_header'] == 1]).sum()
    
    # Non-type strain statistics
    non_type_strain_species_count = len(prod_df[prod_df['is_type_strain_header'] == 0]['species'].unique())
    non_type_strain_prod = count_metabolites(prod_df[prod_df['is_type_strain_header'] == 0]).sum()
    non_type_strain_util = count_metabolites(util_df[prod_df['is_type_strain_header'] == 0]).sum()
    non_type_strain_anti = count_metabolites(anti_df[prod_df['is_type_strain_header'] == 0]).sum()

    # Summing both
    total_species_count = type_strain_species_count + non_type_strain_species_count
    total_prod = type_strain_prod + non_type_strain_prod
    total_util = type_strain_util + non_type_strain_util
    total_anti = type_strain_anti + non_type_strain_anti

    stats.append(['Type Strain', type_strain_species_count, type_strain_prod, type_strain_util, type_strain_anti])
    stats.append(['Non-Type Strain', non_type_strain_species_count, non_type_strain_prod, non_type_strain_util, non_type_strain_anti])
    stats.append(['Total', total_species_count, total_prod, total_util, total_anti])

    stats_df = pd.DataFrame(stats, columns=['Category', 'Species Count', 'Prod Metabolites', 'Util Metabolites', 'Anti Metabolites'])
    return stats_df

# Streamlit App
st.title("Metabolites Overview")

# Always display broad statistics table
st.write("### Broad Statistics for Type and Non-Type Strains")
stats_df = compute_statistics(prod_df, util_df, anti_df)
st.write(stats_df)

# Add checkboxes to filter type strains
st.sidebar.header("Filter by Type Strain")
show_type_strain_1 = st.sidebar.checkbox("Show Type Strain (1)", value=True)
show_type_strain_0 = st.sidebar.checkbox("Show Non-Type Strain (0)", value=True)

# Filter data based on checkboxes
if show_type_strain_1 and not show_type_strain_0:
    prod_df_filtered = filter_by_type_strain(prod_df, 1)
    util_df_filtered = filter_by_type_strain(util_df, 1)
    anti_df_filtered = filter_by_type_strain(anti_df, 1)
elif not show_type_strain_1 and show_type_strain_0:
    prod_df_filtered = filter_by_type_strain(prod_df, 0)
    util_df_filtered = filter_by_type_strain(util_df, 0)
    anti_df_filtered = filter_by_type_strain(anti_df, 0)
else:
    # Show both by default if both checkboxes are checked
    prod_df_filtered = prod_df
    util_df_filtered = util_df
    anti_df_filtered = anti_df

# Sidebar buttons for analysis
st.sidebar.header("Select Analysis")
show_prod_count = st.sidebar.button("Show Production Metabolite Count")
show_util_count = st.sidebar.button("Show Utilization Metabolite Count")
show_anti_count = st.sidebar.button("Show Antimicrobial Metabolite Count")
show_prod_species = st.sidebar.button("Show Top 10 Production Species")
show_util_species = st.sidebar.button("Show Top 10 Utilization Species")
show_anti_species = st.sidebar.button("Show Top 10 Antimicrobial Species")
show_prod_metabolites = st.sidebar.button("Show Top 10 Production Metabolites")
show_util_metabolites = st.sidebar.button("Show Top 10 Utilization Metabolites")
show_anti_metabolites = st.sidebar.button("Show Top 10 Antimicrobial Metabolites")

# Show Production Metabolite Count
if show_prod_count:
    st.write("### Total Production Metabolite Count")
    st.write(count_metabolites(prod_df_filtered))

# Show Utilization Metabolite Count
if show_util_count:
    st.write("### Total Utilization Metabolite Count")
    st.write(count_metabolites(util_df_filtered))

# Show Antimicrobial Metabolite Count
if show_anti_count:
    st.write("### Total Antimicrobial Metabolite Count")
    st.write(count_metabolites(anti_df_filtered))

# Show Top 10 Production Species
if show_prod_species:
    st.write("### Top 10 Species Producing Metabolites")
    st.write(prod_df_filtered['species'].value_counts().head(10))

# Show Top 10 Utilization Species
if show_util_species:
    st.write("### Top 10 Species Utilizing Metabolites")
    st.write(util_df_filtered['species'].value_counts().head(10))

# Show Top 10 Antimicrobial Species
if show_anti_species:
    st.write("### Top 10 Species with Antimicrobial Metabolites")
    st.write(anti_df_filtered['species'].value_counts().head(10))

# Show Top 10 Production Metabolites
if show_prod_metabolites:
    st.write("### Top 10 Production Metabolites")
    st.write(count_metabolites(prod_df_filtered).sort_values(ascending=False).head(10))

# Show Top 10 Utilization Metabolites
if show_util_metabolites:
    st.write("### Top 10 Utilization Metabolites")
    st.write(count_metabolites(util_df_filtered).sort_values(ascending=False).head(10))

# Show Top 10 Antimicrobial Metabolites
if show_anti_metabolites:
    st.write("### Top 10 Antimicrobial Metabolites")
    st.write(count_metabolites(anti_df_filtered).sort_values(ascending=False).head(10))

