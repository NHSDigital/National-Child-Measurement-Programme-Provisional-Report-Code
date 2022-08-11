SELECT
    [AcademicYear],
    [Bmi],
    [BmiPopulationCategory],
    [BmiPScore],
    [NcmpEthnicityCode],
    [NcmpSchoolStatus],
    [NcmpSystemId],
    [NhsEthnicityCode],
    [OrgCode],
    [PupilIndexOfMultipleDeprivationD],
    [SchoolIndexOfMultiDeprivationD],
    [SchoolLowerSuperOutputArea2011],
    [SchoolUrn],
    [SchoolYear]
FROM [DATABASE].[SERVER].[TABLE]
WHERE [AcademicYear] <IY_BASEYEARS>
AND [Bmi] IS NOT NULL
AND [NcmpSchoolStatus] = 'NCMP'