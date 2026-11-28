#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "SteelCityJoystick.generated.h"
class UCanvasPanelSlot;
UCLASS()
class STEELCITY_API USteelCityJoystick : public UUserWidget
{
    GENERATED_BODY()
public:
    FVector2D GetJoystickInput() const { return Input; }
    void ResetInput();
protected:
    virtual TSharedRef<SWidget> RebuildWidget() override;
    virtual FReply NativeOnTouchStarted(const FGeometry&, const FPointerEvent&) override;
    virtual FReply NativeOnTouchMoved(const FGeometry&, const FPointerEvent&) override;
    virtual FReply NativeOnTouchEnded(const FGeometry&, const FPointerEvent&) override;
    virtual void NativeOnMouseCaptureLost(const FCaptureLostEvent&) override;
    virtual void NativeDestruct() override;
private:
    UPROPERTY(Transient) TObjectPtr<UCanvasPanelSlot> ThumbSlot;
    int32 ActivePointer = INDEX_NONE;
    int32 ActiveUser = INDEX_NONE;
    FVector2D Input = FVector2D::ZeroVector;
    void UpdateInput(const FGeometry&, const FPointerEvent&);
};
