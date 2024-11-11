import gc
from src.database.access_mssql import AccessMsSQL
from src.app.mssql.sql_executor import run_sql_query

from config.config import settings

field_mappings = {
    "OSFamily": [
        "OSFamilyId", "ManufacturerId", "OSFamily", "OSFamilyDescription"
    ],
    "OSType": [
        "OSFamilyId", "OSType", "OSTypeId", "OSTypeName", "OrderBy"
    ],
    "MajorOS": [
        "MajorOSId", "OSTypeId", "MajorVersion", "MajorVersionOrder",
        "MajorOSInternalName", "MajorOSShortInternalName", "SupportPolicyId",
        "DataReleaseLevel"
    ],
    "OS": [
        "OSId", "MajorOSId", "Version", "OSReleaseStatus", "VersionOrder",
        "IsRecommended", "SupportStateId", "ReleaseDate", "MaxRawCapacity",
        "MaxVolumePerClusterCount", "MaxActiveVolumePerClusterCount",
        "DataReleaseLevel", "DataClass"
    ],
    "BoundOSAffiliate": [
        "BoundOSAffiliateId", "OSAffiliateId", "OSId", "DataReleaseLevel"
    ],
    "OSAffiliate": [
        "OSAffiliateId", "OSTypeId", "Version", "OSReleaseStatusId", 
        "VersionOrder", "IsRecommended", "SupportStateId", "ReleaseDate", 
        "DataReleaseLevel", "DataClass"
    ],
    "PlatformType": [
        "PlatformTypeId", "ManufacturerId", "PlatformType",
        "PlatformTypeDisplayName", "Description", "IsStorage", "OrderBy"
    ],
    "PlatformFamily": [
        "PlatformFamilyId", "PlatformFamily", "PlatformTypeId",
        "EmbedsInShelf", "OrderBy"
    ],
    "PlatformModel": [
        "PlatformModelId", "PlatformFamilyId", "PlatformModelSystemName",
        "InternalName", "MarketEntryPointId", "MarketingPriorityId",
        "ProcessorTypeId", "ProcessorCount", "MaxEmbeddedDriveCount",
        "MinEmbeddedDriveCount", "MaxPSUCount", "MaxRawCapacity",
        "WAFLAllocationOffsetPerDrive", "WidthWithoutMountingFlanges_cm",
        "WidthWithMountingFlanges_cm", "DepthWithoutCblMgtBracket_cm",
        "DepthWithCblMgtBracket_cm", "FrontClearanceCooling_cm",
        "RearClearanceCooling_cm", "FrontClearanceMaintenance_cm",
        "RearClearanceMaintenance_cm", "OperatingTemperatureMin_C",
        "OperatingTemperatureMax_C", "StorageTemperatureMin_C",
        "StorageTemperatureMax_C", "TransitTemperatureMin_C",
        "TransitTemperatureMax_C", "OperatingRelativeHumidityMin_percent",
        "OperatingRelativeHumidityMax_percent", "StorageRelativeHumidityMin_percent",
        "StorageRelativeHumidityMax_percent", "TransitRelativeHumidityMin_percent",
        "TransitRelativeHumidityMax_percent", "OperatingAltitudeMin_m",
        "OperatingAltitudeMax_m", "StorageAltitudeMin_m", "StorageAltitudeMax_m",
        "TransitAltitudeMin_m", "TransitAltitudeMax_m", "OrderBy",
        "DataReleaseLevel", "DataClass"
    ],
    "PlatformConfig": [
        "PlatformConfigId", "PlatformModelId", "PlatformConfig",
        "PlatformConfigTypeId", "PlatformConfigMarketingDescription",
        "PlatformConfigTechnicalDescription", "EthernetPortCount",
        "EthernetInterfaceId", "FCPortCount", "FCInterfaceId", "CNAPortCount",
        "PCISlotCount", "PCIInterfaceId", "SCSIPortCount", "SCSIInterfaceId",
        "ClientStoragePortCount", "ClientInterfaceId", "HostStoragePortCount",
        "HostInterfaceId", "MgmtPortCount", "MgmtInterfaceId", "MaxBackEndFCLoops",
        "SASPortCount", "SDS_IsEnabled", "SDS_SingleEnclosureCluster",
        "SDS_DefCabinetPrimary", "SDS_DefCabinetSlotPrimary", "SDS_DefCabinetPartner",
        "SDS_DefCabinetSlotPartner", "SDS_CanDrawVisio", "RackUnits", "Height_cm",
        "OrderBy", "DataReleaseLevel", "DataClass"
    ],
    "BoundPlatformOS": [
        "BoundPlatformOSId", "OSId", "PlatformConfigId", "MaxDriveCount",
        "MaxLunCount", "MaxExtDiskShelves", "MaxBackEndFCLoops", "MaxAggrSize32bit",
        "MaxAggrSize64bit", "MaxFlexVolSize32bit", "MaxFlexVolSize64bit",
        "MaxCompositeAggregateSize", "MaxVolumeSize", "IsFlexGroupSupported",
        "InfiniteVolumeDataConstituentSize", "MaxFCShelfTypeDriveCount",
        "MaxSASShelfTypeDriveCount", "SupportsFlashPool", "MaxCache_with_Flash_no_Pool",
        "MaxCache_with_Pool_no_Flash", "MaxCache_with_Flash_and_Pool",
        "MinFlashPoolDriveCountPerAggr", "MaxActiveVolumeCount", "MaxISCSISessionsCount",
        "SupportsArrayLUNs", "ArrayLUNAbsoluteMinRawCapacity", "ArrayLUNBlockSize_Bytes",
        "DefaultArrayLUNRAIDGroupSize", "ArrayLUNMaxRAIDGroupsPerAggregate", 
        "MaxArrayLUNSize", "MaxArrayLUNRAIDGroupSize", "MinArrayLUNSize", 
        "MinArrayLUNRootVolSize", "MinArrayLUNRAIDGroupSize", "MinArrayLUNAggregateSize",
        "ArrayLUNneighborhoodVisibleAssignedDevices", "ArrayLUNRecommendedMinRawCapacity",
        "SpareCoreArrayLUNMinSize", "MaxVirtualDiskSize_GB", "VirtualEthernetPortCount",
        "Eseries_MaxDestagingCachetoFlashSize", "Eseries_MaxVolumeSize",
        "Eseries_DDPsupport", "Eseries_SSDSupportInDiskPool",
        "Eseries_MaxDrivesPerDiskPool", "Eseries_MaxDiskPoolVolumes",
        "Eseries_MaxVolSizeForDiskPoolVolume", "Eseries_MaxDiskPools",
        "MaxSystemDynamicDiskPoolCapacity", "Eseries_MaxPartitions",
        "Eseries_MaxVolumesPerPartition", "Eseries_FlashReadCacheSupport",
        "Eseries_MinFlashReadCacheCapacity", "Eseries_MaxFlashReadCacheCapacity",
        "Eseries_FDESupport", "Eseries_T10PISupport", "MaxVCPUCoresAllowed",
        "MaxIOPs", "MaxStorageThroughput", "MaxBackupThroughput_GBperHr",
        "DataReleaseLevel"
    ],
    "SoftwareLimitType": [
        "SoftwareLimitTypeId", "SoftwareLimitType", "SoftwareLimitTypeDescription", "OrderBy"
    ],
    "BaseSoftwareLimits": [
        "BaseSoftwareLimitsId", "SoftwareLimitName", "SoftwareLimitTypeId",
        "StorageArchitectureStackId", "SoftwareLimitSystemName",
        "SoftwareLimitDescription", "OrderBy", "DataReleaseLevel", "DataClass"
    ],
    "StorageArchitectureStack": [
        "StorageArchitectureStackId", "StorageArchitectureStackName"
    ],
    "SoftwareLimits": [
        "SoftwareLimitsId", "BaseSoftwareLimitsId", "SoftwareLimitScopeId",
        "ClusterSizeId", "IsCodeEnforced", "DataReleaseLevel", "DataClass"
    ],
    "SoftwareLimitScope": [
        "SoftwareLimitScopeId", "SoftwareLimitScope", "SoftwareLimitScopeDescription", "OrderBy"
    ],
    "BoundPlatformOSSoftwareLimits": [
        "BoundPlatformOSSoftwareLimitsId", "BoundPlatformOSId", "SoftwareLimitsId",
        "LimitValue", "DataClass", "DataReleaseLevel"
    ]
}


class SqlConnector:
    def __init__(self, username: str, password: str, driver: str, server: str):
        self.db_connection = AccessMsSQL(username=username, password=password, db_driver=driver, db_server=server)
 
    async def get_connection_string(self) -> str:
        return await self.db_connection.main()
    
async def fetch_data():
    sql_connector = SqlConnector(
        username=settings.mssql.USERNAME,
        password=settings.mssql.PASSWORD,
        driver=settings.mssql.DRIVER,
        server=settings.mssql.SERVER
    )
    connection_string = await sql_connector.get_connection_string()
    
    for key, value in field_mappings.items():
        columns = ', '.join(value)
        sql_query = f"SELECT {columns} FROM dbo.{key}"
        success, output_df = await run_sql_query(connection_string=connection_string, sql_query=sql_query)
        if success and not output_df.empty:
            if key == "BoundPlatformOSSoftwareLimits":
                output_df.to_csv("./dataBoundPlatformOSSoftwareLimits.csv", index=False)
                chunk_size = 100000
                for i, chunk in enumerate(range(0, len(output_df),  chunk_size)):
                    chunk_df = output_df.iloc[chunk:chunk +  chunk_size]
                    file_name = f"./data/{key}_{i+1}.csv"
                    chunk_df.to_csv(file_name, index=False)
                    print(f"Saved {file_name} with shape {chunk_df.shape}")
            else:            
                file_name = f"data/{key}.csv"
                output_df.to_csv(file_name, index = False)
                print(f"Saved {file_name} with shape {output_df.shape}")
                
        gc.collect()
                
if __name__ == "__main__":
    import asyncio
    asyncio.run(fetch_data())