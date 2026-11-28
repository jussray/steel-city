#include "SteelCityHUD.h"
#include "SteelCityGameState.h"
#include "Components/TextBlock.h"
#include "Engine/World.h"
void USteelCityHUD::NativeConstruct()
{
    Super::NativeConstruct();
    RefreshBinding();
}
void USteelCityHUD::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
    Super::NativeTick(MyGeometry, InDeltaTime);
    // State may arrive after a local widget is constructed or change during travel.
    RefreshBinding();
}
void USteelCityHUD::NativeDestruct()
{
    UnbindState();
    Super::NativeDestruct();
}
void USteelCityHUD::UnbindState()
{
    if (ASteelCityGameState* State = BoundState.Get())
        State->OnStarsChanged.RemoveDynamic(this, &USteelCityHUD::HandleStarsChanged);
    BoundState.Reset();
}
void USteelCityHUD::RefreshBinding()
{
    ASteelCityGameState* State = GetWorld() ? GetWorld()->GetGameState<ASteelCityGameState>() : nullptr;
    if (State == BoundState.Get()) return;
    UnbindState();
    if (!State) return;
    BoundState = State;
    State->OnStarsChanged.AddUniqueDynamic(this, &USteelCityHUD::HandleStarsChanged);
    HandleStarsChanged(State->StarsCollected);
}
void USteelCityHUD::HandleStarsChanged(int32 Count)
{
    if (StarCountText)
        StarCountText->SetText(FText::Format(NSLOCTEXT("SteelCity", "StarCount", "{0}/{1}"),
            FText::AsNumber(Count), FText::AsNumber(FSteelCityStarLedger::Target)));
}
