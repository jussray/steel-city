#pragma once
#include "CoreMinimal.h"
// Pure gameplay rules; seven known pickup identities, any five accepted.
struct FSteelCityStarLedger
{
    static constexpr int32 Target = 5;
    static constexpr int32 Locations = 7;
    bool TryCollect(FName Id)
    {
        if (Ids.Num() >= Target || Ids.Contains(Id)) return false;
        bool bKnown = false;
        for (int32 Index = 1; Index <= Locations; ++Index)
        {
            if (Id == FName(*FString::Printf(TEXT("steel-star-%d"), Index))) { bKnown = true; break; }
        }
        if (!bKnown) return false;
        Ids.Add(Id);
        return true;
    }
    int32 Count() const { return Ids.Num(); }
    void Reset() { Ids.Reset(); }
private:
    TSet<FName> Ids;
};
