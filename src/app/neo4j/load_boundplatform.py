import asyncio
from retry import retry
from time import perf_counter
from typing import List, Dict, Tuple, Any

from config.config import settings
from src.database.access_mssql import AccessMsSQL
from src.database.access_neo4j import AccessNeo4j
from utils.unique_constraints import _set_uniqueness_constraints

def log_time(start, step):
    print(f"{step} execution time : {perf_counter() - start:.2f} seconds")

@retry(tries=3, delay=10)
async def load_bound0s_data():
    neo4j_connection = AccessNeo4j(uri=settings.neo4j.NEO4J_URI, username=settings.neo4j.NEO4J_USERNAME, password=settings.neo4j.NEO4J_PASSWORD)
    neo4j_driver = await neo4j_connection.main()

    with neo4j_driver.session(database="neo4j") as session:
        for node in settings.boundplatform.NODES:
            session.execute_write(_set_uniqueness_constraints, node)

    async def create_relationships(session):
        relationships = [
            ("OSFamily", "OSType", "HAS_TYPE", "OSFamilyId"),
            ("OSType", "MajorOS", "HAS_MAJOR_OS", "OSTypeId"),
            ("OSType", "OSAffiliate", "HAS_AFFILIATE", "OSTypeId"),
            ("OSAffiliate", "BoundOSAffiliate", "HAS_BOUND_AFFILIATE", "OSAffiliateId"),
            ("MajorOS", "OS", "HAS_OS", "MajorOSId"),
            ("BoundOSAffiliate", "OS", "HAS_BOUND_OS", "BoundOSAffiliateId"),
            ("PlatformType", "PlatformFamily", "HAS_FAMILY", "PlatformTypeId"),
            ("PlatformFamily", "PlatformModel", "HAS_MODEL", "PlatformFamilyId"),
            ("PlatformModel", "PlatformConfig", "HAS_CONFIG", "PlatformModelId"),
            ("SoftwareLimitType", "BaseSoftwareLimits", "HAS_BASE_LIMIT", "SoftwareLimitTypeId"),
            ("SoftwareArchitectureStack", "BaseSoftwareLimits", "USES_LIMIT", "SoftwareArchitectureStackId"),
            ("BaseSoftwareLimits", "SoftwareLimits", "INCLUDES_LIMIT", "BaseLimitId"),
            ("SoftwareLimitScope", "SoftwareLimits", "APPLIES_TO_SCOPE", "ScopeId"),
            # ("SoftwareLimits", "BoundPlatformOSSoftwareLimits", "APPLIES_LIMIT", "LimitId"),
            # ("BoundPlatformOS", "BoundPlatformOSSoftwareLimits", "HAS_BOUND_LIMIT", "BoundPlatformOSId"),
            # ("PlatformConfig", "BoundPlatformOS", "CONFIGURED_FOR", "PlatformConfigId"),
        ]

        for start_node, end_node, relationship, key in relationships:
            start_time = perf_counter()
            query = f"""
                MATCH (a:{start_node}), (b:{end_node})
                WHERE a.{key} = b.{key}
                MERGE (a)-[r:{relationship}]->(b)
            """
            session.run(query)
            log_time(start=start_time, step=f"{start_node} to {end_node} ({relationship})")
            
    start_time =  perf_counter()
    with neo4j_driver.session(database="neo4j") as session:
        query = """
        LOAD CSV WITH HEADERS FROM 'file:///OSFamily.csv' AS osfamily
        MERGE (os:OSFamily {
            OSFamilyId: toInteger(osfamily.OSFamilyId)
        })
        ON CREATE SET
            os.ManufacturerId = osfamily.ManufacturerId,
            os.OSFamily = osfamily.OSFamily,
            os.OSFamilyDescription = CASE WHEN osfamily.OSFamilyDescription IS NOT NULL THEN osfamily.OSFamilyDescription ELSE 'Unknown' END
        """
        _ = session.run(query)
    log_time(start=start_time, step="OSFamily")

    start_time =  perf_counter()
    with neo4j_driver.session(database="neo4j") as session:
        query = """
        LOAD CSV WITH HEADERS FROM 'file:///OSType.csv' AS ostype
        MERGE (ot:OSType {
            OSTypeId: toInteger(ostype.OSTypeId)
        })
        ON CREATE SET
            ot.OSFamilyId = toInteger(ostype.OSFamilyId),
            ot.OSType = ostype.OSType,
            ot.OSTypeName = ostype.OSTypeName,
            ot.OrderBy = toInteger(ostype.OrderBy)
        """
        _ = session.run(query)
    log_time(start=start_time, step="OSType")
    
    start_time =  perf_counter()
    with neo4j_driver.session(database="neo4j") as session:
        query = """
        LOAD CSV WITH HEADERS FROM 'file:///MajorOS.csv' AS majoros
        MERGE (mos:MajorOS {
            MajorOSId: toInteger(majoros.MajorOSId)
        })
        ON CREATE SET
            mos.OSTypeId = toInteger(majoros.OSTypeId),
            mos.MajorVersion = majoros.MajorVersion,
            mos.MajorVersionOrder = toInteger(majoros.MajorVersionOrder),
            mos.MajorOSInternalName = majoros.MajorOSInternalName,
            mos.MajorOSShortInternalName = majoros.MajorOSShortInternalName,
            mos.SupportPolicyId = toInteger(majoros.SupportPolicyId),
            mos.DataReleaseLevel = majoros.DataReleaseLevel
        """
        _ = session.run(query)
    log_time(start=start_time, step="MajorOS")
    
    # start_time =  perf_counter()
    # with neo4j_driver.session(database="neo4j") as session:
    #     query = """
    #     LOAD CSV WITH HEADERS FROM 'file:///OS.csv' AS os
    #     MERGE (os_node:OS {
    #         OSId: toInteger(os.OSId)
    #     })
    #     ON CREATE SET
    #         os_node.MajorOSId = toInteger(os.MajorOSId),
    #         os_node.Version = os.Version,
    #         os_node.OSReleaseStatus = os.OSReleaseStatus,
    #         os_node.VersionOrder = toInteger(os.VersionOrder),
    #         os_node.IsRecommended = toBoolean(os.IsRecommended),
    #         os_node.SupportStateId = toInteger(os.SupportStateId),
    #         os_node.ReleaseDate = date(os.ReleaseDate),
    #         os_node.MaxRawCapacity = toInteger(os.MaxRawCapacity),
    #         os_node.MaxVolumePerClusterCount = toInteger(os.MaxVolumePerClusterCount),
    #         os_node.MaxActiveVolumePerClusterCount = toInteger(os.MaxActiveVolumePerClusterCount),
    #         os_node.DataReleaseLevel = os.DataReleaseLevel,
    #         os_node.DataClass = os.DataClass
    #     """
    #     _ = session.run(query)
    # log_time(start=start_time, step="OS")
    
    start_time =  perf_counter()
    with neo4j_driver.session(database="neo4j") as session:
        query = """
        LOAD CSV WITH HEADERS FROM 'file:///BoundOSAffiliate.csv' AS boundosaffiliate
        MERGE (baff:BoundOSAffiliate {
            BoundOSAffiliateId: toInteger(boundosaffiliate.BoundOSAffiliateId)
        })
        ON CREATE SET
            baff.OSAffiliateId = toInteger(boundosaffiliate.OSAffiliateId),
            baff.OSId = toInteger(boundosaffiliate.OSId),
            baff.DataReleaseLevel = boundosaffiliate.DataReleaseLevel
        """
        _ = session.run(query)
    log_time(start=start_time, step="BoundOSAffiliate")
    
    start_time =  perf_counter()
    with neo4j_driver.session(database="neo4j") as session:
        query = """
        LOAD CSV WITH HEADERS FROM 'file:///OSAffiliate.csv' AS osaffiliate
        MERGE (osa:OSAffiliate {
            OSAffiliateId: toInteger(osaffiliate.OSAffiliateId)
        })
        ON CREATE SET
            osa.OSTypeId = toInteger(osaffiliate.OSTypeId),
            osa.Version = osaffiliate.Version,
            osa.OSReleaseStatusId = toInteger(osaffiliate.OSReleaseStatusId),
            osa.VersionOrder = toInteger(osaffiliate.VersionOrder),
            osa.IsRecommended = toBoolean(osaffiliate.IsRecommended),
            osa.SupportStateId = toInteger(osaffiliate.SupportStateId),
            osa.ReleaseDate = date(osaffiliate.ReleaseDate),
            osa.DataReleaseLevel = osaffiliate.DataReleaseLevel,
            osa.DataClass = osaffiliate.DataClass
        """
        _ = session.run(query)
    log_time(start=start_time, step="OSAffiliate")
    
    start_time =  perf_counter()
    with neo4j_driver.session(database="neo4j") as session:
        query = """
        LOAD CSV WITH HEADERS FROM 'file:///PlatformType.csv' AS platformtype
        MERGE (pt:PlatformType {
            PlatformTypeId: toInteger(platformtype.PlatformTypeId)
        })
        ON CREATE SET
            pt.ManufacturerId = toInteger(platformtype.ManufacturerId),
            pt.PlatformType = platformtype.PlatformType,
            pt.PlatformTypeDisplayName = platformtype.PlatformTypeDisplayName,
            pt.Description = platformtype.Description,
            pt.IsStorage = toBoolean(platformtype.IsStorage),
            pt.OrderBy = toInteger(platformtype.OrderBy)
        """
        _ = session.run(query)
    log_time(start=start_time, step="PlatformType")
    
    start_time =  perf_counter()
    with neo4j_driver.session(database="neo4j") as session:
        query = """
        LOAD CSV WITH HEADERS FROM 'file:///PlatformFamily.csv' AS platformfamily
        MERGE (pf:PlatformFamily {
            PlatformFamilyId: toInteger(platformfamily.PlatformFamilyId)
        })
        ON CREATE SET
            pf.PlatformFamily = platformfamily.PlatformFamily,
            pf.PlatformTypeId = toInteger(platformfamily.PlatformTypeId),
            pf.EmbedsInShelf = toBoolean(platformfamily.EmbedsInShelf),
            pf.OrderBy = toInteger(platformfamily.OrderBy)
        """
        _ = session.run(query)
    log_time(start=start_time, step="PlatformFamily")
    
    start_time =  perf_counter()
    with neo4j_driver.session(database="neo4j") as session:
        query = """
        LOAD CSV WITH HEADERS FROM 'file:///PlatformModel.csv' AS platformmodel
        MERGE (pm:PlatformModel {
            PlatformModelId: toInteger(platformmodel.PlatformModelId)
        })
        ON CREATE SET
            pm.PlatformFamilyId = toInteger(platformmodel.PlatformFamilyId),
            pm.PlatformModelSystemName = platformmodel.PlatformModelSystemName,
            pm.InternalName = platformmodel.InternalName,
            pm.MarketEntryPointId = toInteger(platformmodel.MarketEntryPointId),
            pm.MarketingPriorityId = toInteger(platformmodel.MarketingPriorityId),
            pm.ProcessorTypeId = toInteger(platformmodel.ProcessorTypeId),
            pm.ProcessorCount = toInteger(platformmodel.ProcessorCount),
            pm.MaxEmbeddedDriveCount = toInteger(platformmodel.MaxEmbeddedDriveCount),
            pm.MinEmbeddedDriveCount = toInteger(platformmodel.MinEmbeddedDriveCount),
            pm.MaxPSUCount = toInteger(platformmodel.MaxPSUCount),
            pm.MaxRawCapacity = toInteger(platformmodel.MaxRawCapacity),
            pm.WAFLAllocationOffsetPerDrive = toInteger(platformmodel.WAFLAllocationOffsetPerDrive),
            pm.WidthWithoutMountingFlanges_cm = toFloat(platformmodel.WidthWithoutMountingFlanges_cm),
            pm.WidthWithMountingFlanges_cm = toFloat(platformmodel.WidthWithMountingFlanges_cm),
            pm.DepthWithoutCblMgtBracket_cm = toFloat(platformmodel.DepthWithoutCblMgtBracket_cm),
            pm.DepthWithCblMgtBracket_cm = toFloat(platformmodel.DepthWithCblMgtBracket_cm),
            pm.FrontClearanceCooling_cm = toFloat(platformmodel.FrontClearanceCooling_cm),
            pm.RearClearanceCooling_cm = toFloat(platformmodel.RearClearanceCooling_cm),
            pm.FrontClearanceMaintenance_cm = toFloat(platformmodel.FrontClearanceMaintenance_cm),
            pm.RearClearanceMaintenance_cm = toFloat(platformmodel.RearClearanceMaintenance_cm),
            pm.OperatingTemperatureMin_C = toFloat(platformmodel.OperatingTemperatureMin_C),
            pm.OperatingTemperatureMax_C = toFloat(platformmodel.OperatingTemperatureMax_C),
            pm.StorageTemperatureMin_C = toFloat(platformmodel.StorageTemperatureMin_C),
            pm.StorageTemperatureMax_C = toFloat(platformmodel.StorageTemperatureMax_C),
            pm.TransitTemperatureMin_C = toFloat(platformmodel.TransitTemperatureMin_C),
            pm.TransitTemperatureMax_C = toFloat(platformmodel.TransitTemperatureMax_C),
            pm.OperatingRelativeHumidityMin_percent = toFloat(platformmodel.OperatingRelativeHumidityMin_percent),
            pm.OperatingRelativeHumidityMax_percent = toFloat(platformmodel.OperatingRelativeHumidityMax_percent),
            pm.StorageRelativeHumidityMin_percent = toFloat(platformmodel.StorageRelativeHumidityMin_percent),
            pm.StorageRelativeHumidityMax_percent = toFloat(platformmodel.StorageRelativeHumidityMax_percent),
            pm.TransitRelativeHumidityMin_percent = toFloat(platformmodel.TransitRelativeHumidityMin_percent),
            pm.TransitRelativeHumidityMax_percent = toFloat(platformmodel.TransitRelativeHumidityMax_percent),
            pm.OperatingAltitudeMin_m = toInteger(platformmodel.OperatingAltitudeMin_m),
            pm.OperatingAltitudeMax_m = toInteger(platformmodel.OperatingAltitudeMax_m),
            pm.StorageAltitudeMin_m = toInteger(platformmodel.StorageAltitudeMin_m),
            pm.StorageAltitudeMax_m = toInteger(platformmodel.StorageAltitudeMax_m),
            pm.TransitAltitudeMin_m = toInteger(platformmodel.TransitAltitudeMin_m),
            pm.TransitAltitudeMax_m = toInteger(platformmodel.TransitAltitudeMax_m),
            pm.OrderBy = toInteger(platformmodel.OrderBy),
            pm.DataReleaseLevel = platformmodel.DataReleaseLevel,
            pm.DataClass = platformmodel.DataClass
        """
        _ = session.run(query)
    log_time(start=start_time, step="PlatformModel")
    
    # start_time =  perf_counter()
    # with neo4j_driver.session(database="neo4j") as session:
    #     query = """
    #     LOAD CSV WITH HEADERS FROM 'file:///PlatformConfig.csv' AS platformconfig
    #     MERGE (pc:PlatformConfig {
    #         PlatformConfigId: toInteger(platformconfig.PlatformConfigId)
    #     })
    #     ON CREATE SET
    #         pc.PlatformModelId = toInteger(platformconfig.PlatformModelId),
    #         pc.PlatformConfig = platformconfig.PlatformConfig,
    #         pc.PlatformConfigTypeId = toInteger(platformconfig.PlatformConfigTypeId),
    #         pc.PlatformConfigMarketingDescription = platformconfig.PlatformConfigMarketingDescription,
    #         pc.PlatformConfigTechnicalDescription = platformconfig.PlatformConfigTechnicalDescription,
    #         pc.EthernetPortCount = toInteger(platformconfig.EthernetPortCount),
    #         pc.EthernetInterfaceId = toInteger(platformconfig.EthernetInterfaceId),
    #         pc.FCPortCount = toInteger(platformconfig.FCPortCount),
    #         pc.FCInterfaceId = toInteger(platformconfig.FCInterfaceId),
    #         pc.CNAPortCount = toInteger(platformconfig.CNAPortCount),
    #         pc.PCISlotCount = toInteger(platformconfig.PCISlotCount),
    #         pc.PCIInterfaceId = toInteger(platformconfig.PCIInterfaceId),
    #         pc.SCSIPortCount = toInteger(platformconfig.SCSIPortCount),
    #         pc.SCSIInterfaceId = toInteger(platformconfig.SCSIInterfaceId),
    #         pc.ClientStoragePortCount = toInteger(platformconfig.ClientStoragePortCount),
    #         pc.ClientInterfaceId = toInteger(platformconfig.ClientInterfaceId),
    #         pc.HostStoragePortCount = toInteger(platformconfig.HostStoragePortCount),
    #         pc.HostInterfaceId = toInteger(platformconfig.HostInterfaceId),
    #         pc.MgmtPortCount = toInteger(platformconfig.MgmtPortCount),
    #         pc.MgmtInterfaceId = toInteger(platformconfig.MgmtInterfaceId),
    #         pc.MaxBackEndFCLoops = toInteger(platformconfig.MaxBackEndFCLoops),
    #         pc.SASPortCount = toInteger(platformconfig.SASPortCount),
    #         pc.SDS_IsEnabled = toBoolean(platformconfig.SDS_IsEnabled),
    #         pc.SDS_SingleEnclosureCluster = toBoolean(platformconfig.SDS_SingleEnclosureCluster),
    #         pc.SDS_DefCabinetPrimary = platformconfig.SDS_DefCabinetPrimary,
    #         pc.SDS_DefCabinetSlotPrimary = toInteger(platformconfig.SDS_DefCabinetSlotPrimary),
    #         pc.SDS_DefCabinetPartner = platformconfig.SDS_DefCabinetPartner,
    #         pc.SDS_DefCabinetSlotPartner = toInteger(platformconfig.SDS_DefCabinetSlotPartner),
    #         pc.SDS_CanDrawVisio = toBoolean(platformconfig.SDS_CanDrawVisio),
    #         pc.RackUnits = toInteger(platformconfig.RackUnits),
    #         pc.Height_cm = toFloat(platformconfig.Height_cm),
    #         pc.OrderBy = toInteger(platformconfig.OrderBy),
    #         pc.DataReleaseLevel = platformconfig.DataReleaseLevel,
    #         pc.DataClass = platformconfig.DataClass
    #     """
    #     _ = session.run(query)
    # log_time(start=start_time, step="PlatformConfig")
    
    start_time =  perf_counter()
    with neo4j_driver.session(database="neo4j") as session:
        query = """
        LOAD CSV WITH HEADERS FROM 'file:///SoftwareLimitType.csv' AS softwarelimittype
        MERGE (slt:SoftwareLimitType {
            SoftwareLimitTypeId: toInteger(softwarelimittype.SoftwareLimitTypeId)
        })
        ON CREATE SET
            slt.SoftwareLimitType = softwarelimittype.SoftwareLimitType,
            slt.SoftwareLimitTypeDescription = softwarelimittype.SoftwareLimitTypeDescription,
            slt.OrderBy = toInteger(softwarelimittype.OrderBy)
        """
        _ = session.run(query)
    log_time(start=start_time, step="SoftwareLimitType")
    
    start_time =  perf_counter()
    with neo4j_driver.session(database="neo4j") as session:
        query = """
        LOAD CSV WITH HEADERS FROM 'file:///BaseSoftwareLimits.csv' AS basesoftwarelimits
        MERGE (bsl:BaseSoftwareLimits {
            BaseSoftwareLimitsId: toInteger(basesoftwarelimits.BaseSoftwareLimitsId)
        })
        ON CREATE SET
            bsl.SoftwareLimitName = basesoftwarelimits.SoftwareLimitName,
            bsl.SoftwareLimitTypeId = toInteger(basesoftwarelimits.SoftwareLimitTypeId),
            bsl.StorageArchitectureStackId = toInteger(basesoftwarelimits.StorageArchitectureStackId),
            bsl.SoftwareLimitSystemName = basesoftwarelimits.SoftwareLimitSystemName,
            bsl.SoftwareLimitDescription = basesoftwarelimits.SoftwareLimitDescription,
            bsl.OrderBy = toInteger(basesoftwarelimits.OrderBy),
            bsl.DataReleaseLevel = basesoftwarelimits.DataReleaseLevel,
            bsl.DataClass = basesoftwarelimits.DataClass
        """
        _ = session.run(query)
    log_time(start=start_time, step="BaseSoftwareLimits")
    
    start_time =  perf_counter()
    with neo4j_driver.session(database="neo4j") as session:
        query = """
        LOAD CSV WITH HEADERS FROM 'file:///StorageArchitectureStack.csv' AS storagearchitecturesstack
        MERGE (sas:StorageArchitectureStack {
            StorageArchitectureStackId: toInteger(storagearchitecturesstack.StorageArchitectureStackId)
        })
        ON CREATE SET
            sas.StorageArchitectureStackName = storagearchitecturesstack.StorageArchitectureStackName
        """
        _ = session.run(query)
    log_time(start=start_time, step="StorageArchitectureStack")
    
    # start_time =  perf_counter()
    # with neo4j_driver.session(database="neo4j") as session:
    #     query = """
    #     LOAD CSV WITH HEADERS FROM 'file:///SoftwareLimits.csv' AS softwarelimits
    #     MERGE (sl:SoftwareLimits {
    #         SoftwareLimitsId: toInteger(softwarelimits.SoftwareLimitsId)
    #     })
    #     ON CREATE SET
    #         sl.BaseSoftwareLimitsId = toInteger(softwarelimits.BaseSoftwareLimitsId),
    #         sl.SoftwareLimitScopeId = toInteger(softwarelimits.SoftwareLimitScopeId),
    #         sl.ClusterSizeId = toInteger(softwarelimits.ClusterSizeId),
    #         sl.IsCodeEnforced = toBoolean(softwarelimits.IsCodeEnforced),
    #         sl.DataReleaseLevel = softwarelimits.DataReleaseLevel,
    #         sl.DataClass = softwarelimits.DataClass
    #     """
    #     _ = session.run(query)
    # log_time(start=start_time, step="SoftwareLimits")

    start_time =  perf_counter()
    with neo4j_driver.session(database="neo4j") as session:
        query = """
        LOAD CSV WITH HEADERS FROM 'file:///SoftwareLimitScope.csv' AS softwarelimitscope
        MERGE (sls:SoftwareLimitScope {
            SoftwareLimitScopeId: toInteger(softwarelimitscope.SoftwareLimitScopeId)
        })
        ON CREATE SET
            sls.SoftwareLimitScope = softwarelimitscope.SoftwareLimitScope,
            sls.SoftwareLimitScopeDescription = softwarelimitscope.SoftwareLimitScopeDescription,
            sls.OrderBy = toInteger(softwarelimitscope.OrderBy)
        """
        _ = session.run(query)
    log_time(start=start_time, step="SoftwareLimitScope")
    
    start_time = perf_counter()
    with  neo4j_driver.session(database="neo4j") as session:
        await create_relationships(session=session)
    log_time(start=start_time, step="Relationship")
if __name__ == "__main__":
    asyncio.run(load_bound0s_data())


