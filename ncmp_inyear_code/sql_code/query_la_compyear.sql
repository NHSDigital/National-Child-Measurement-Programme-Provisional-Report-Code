SELECT [AcademicYear],
    [SchoolYear],
    [OrgCode],
    [NcmpSystemId]
FROM [DATABASE].[SERVER].[TABLE]
WHERE [AcademicYear] <IY_COMPYEAR>
AND [Bmi] IS NOT NULL
AND [NcmpSchoolStatus] = 'NCMP'