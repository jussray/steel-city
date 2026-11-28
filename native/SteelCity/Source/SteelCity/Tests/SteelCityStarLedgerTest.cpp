#include "SteelCityStarLedger.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSteelCityLedgerTest, "SteelCity.Gameplay.StarLedger",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FSteelCityLedgerTest::RunTest(const FString&)
{
    FSteelCityStarLedger Ledger;
    TestEqual(TEXT("Starts empty"), Ledger.Count(), 0);
    TestFalse(TEXT("Unknown ID rejected"), Ledger.TryCollect(FName(TEXT("unknown"))));
    TestTrue(TEXT("Alternate pickup accepted"), Ledger.TryCollect(FName(TEXT("steel-star-7"))));
    TestFalse(TEXT("Duplicate rejected"), Ledger.TryCollect(FName(TEXT("steel-star-7"))));
    for (int32 I = 1; I <= 4; ++I)
        TestTrue(TEXT("Distinct pickup accepted"), Ledger.TryCollect(FName(*FString::Printf(TEXT("steel-star-%d"), I))));
    TestEqual(TEXT("Target reached"), Ledger.Count(), 5);
    TestFalse(TEXT("Sixth pickup rejected"), Ledger.TryCollect(FName(TEXT("steel-star-5"))));
    Ledger.Reset();
    TestEqual(TEXT("Reset clears ledger"), Ledger.Count(), 0);
    TestTrue(TEXT("Pickup can be collected after reset"), Ledger.TryCollect(FName(TEXT("steel-star-7"))));
    return true;
}
#endif
