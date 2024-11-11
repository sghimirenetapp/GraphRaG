import pandas as pd

# Define a function for loading, merging, renaming, and saving data
def load_and_merge(file1, cols1, file2, cols2, merge_on, rename_map, output_file):
    df1 = pd.read_csv(file1)[cols1]
    df2 = pd.read_csv(file2)[cols2]
    
    merged_df = pd.merge(df1, df2, on=merge_on, how='inner')
    merged_df.rename(columns=rename_map, inplace=True)
    
    merged_df.to_csv(output_file, index=False)
    return merged_df

# Define a function for renaming and saving files
def rename_and_save(file, rename_map, output_file):
    df = pd.read_csv(file)
    df.rename(columns=rename_map, inplace=True)
    df.to_csv(output_file, index=False)
    return df

# Merging and renaming files as needed
# 1. SoftwareLimits and BoundPlatformOSSoftwareLimits
merged_software_limits = load_and_merge(
    "data/SoftwareLimits.csv", ["SoftwareLimitsId"],
    "data/BoundPlatformOSSoftwareLimits.csv", ["BoundPlatformOSSoftwareLimitsId", "SoftwareLimitsId", "LimitValue"],
    merge_on="SoftwareLimitsId",
    rename_map={
        "BoundPlatformOSSoftwareLimitsId": ":END_ID(BoundPlatformOSSoftwareLimits-Id)",
        "SoftwareLimitsId": ":START_ID(SoftwareLimits-Id)"
    },
    output_file="./data/APPLIES_LIMIT.csv"
)

# Final CSVs for SoftwareLimits and BoundPlatformOSSoftwareLimits
rename_and_save("data/SoftwareLimits.csv", {"SoftwareLimitsId": "SoftwareLimitsId:ID(SoftwareLimits-Id)"}, "./data/SoftwareLimits_final.csv")
rename_and_save("data/BoundPlatformOSSoftwareLimits.csv", {"BoundPlatformOSSoftwareLimitsId": "BoundPlatformOSSoftwareLimitsId:ID(BoundPlatformOSSoftwareLimits-Id)"}, "./data/BoundPlatformOSSoftwareLimits_final.csv")

# 2. PlatformConfig and BoundPlatformOS
merged_platform_config = load_and_merge(
    "data/PlatformConfig.csv", ["PlatformConfigId"],
    "data/BoundPlatformOS.csv", ["BoundPlatformOSId", "PlatformConfigId"],
    merge_on="PlatformConfigId",
    rename_map={
        "PlatformConfigId": ":START_ID(PlatformConfig-Id)",
        "BoundPlatformOSId": ":END_ID(BoundPlatformOS-Id)"
    },
    output_file="./data/CONFIGURED_FOR.csv"
)

# Final CSV for PlatformConfig
rename_and_save("data/PlatformConfig.csv", {"PlatformConfigId": "PlatformConfigId:ID(PlatformConfig-Id)"}, "./data/PlatformConfig_final.csv")

# 3. BoundPlatformOS and BoundPlatformOSSoftwareLimits
merged_bound_limits = load_and_merge(
    "data/BoundPlatformOS.csv", ["BoundPlatformOSId"],
    "data/BoundPlatformOSSoftwareLimits.csv", ["BoundPlatformOSSoftwareLimitsId", "BoundPlatformOSId"],
    merge_on="BoundPlatformOSId",
    rename_map={
        "BoundPlatformOSSoftwareLimitsId": ":END_ID(BoundPlatformOSSoftwareLimits-Id)",
        "BoundPlatformOSId": ":START_ID(BoundPlatformOS-Id)"
    },
    output_file="./data/HAS_BOUND_LIMIT.csv"
)

# Final CSV for BoundPlatformOS
rename_and_save("data/BoundPlatformOS.csv", {"BoundPlatformOSId": "BoundPlatformOSId:ID(BoundPlatformOS-Id)"}, "./data/BoundPlatformOS_final.csv")

# 4. OS and BoundPlatformOS
merged_os_platform = load_and_merge(
    "data/OS.csv", ["OSId"],
    "data/BoundPlatformOS.csv", ["BoundPlatformOSId", "OSId"],
    merge_on="OSId",
    rename_map={
        "OSId": ":START_ID(OS-Id)",
        "BoundPlatformOSId": ":END_ID(BoundPlatformOS-Id)"
    },
    output_file="./data/HAS_BOUNDPLATFORM_OS.csv"
)

# Final CSV for OS
rename_and_save("data/OS.csv", {"OSId": "OSId:ID(OS-Id)"}, "./data/OS_final.csv")