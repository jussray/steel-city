#include "SteelCityJoystick.h"
#include "Blueprint/WidgetTree.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Border.h"
#include "Input/Reply.h"
#include "Input/Events.h"
TSharedRef<SWidget> USteelCityJoystick::RebuildWidget()
{
    if (!WidgetTree) WidgetTree = NewObject<UWidgetTree>(this, TEXT("WidgetTree"), RF_Transient);
    if (!WidgetTree->RootWidget)
    {
        UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>();
        WidgetTree->RootWidget = Root;
        UBorder* Base = WidgetTree->ConstructWidget<UBorder>();
        Base->SetBrushColor(FLinearColor(.035f,.075f,.15f,.65f));
        Base->SetVisibility(ESlateVisibility::HitTestInvisible);
        UCanvasPanelSlot* BaseSlot = Root->AddChildToCanvas(Base);
        BaseSlot->SetAnchors(FAnchors(0.f,0.f,1.f,1.f));
        BaseSlot->SetOffsets(FMargin(0.f));
        UBorder* Thumb = WidgetTree->ConstructWidget<UBorder>();
        Thumb->SetBrushColor(FLinearColor(.8f,.95f,1.f,.8f));
        Thumb->SetVisibility(ESlateVisibility::HitTestInvisible);
        ThumbSlot = Root->AddChildToCanvas(Thumb);
        ThumbSlot->SetAnchors(FAnchors(.5f,.5f));
        ThumbSlot->SetAlignment(FVector2D(.5f,.5f));
        ThumbSlot->SetSize(FVector2D(48.f,48.f));
        ThumbSlot->SetPosition(FVector2D::ZeroVector);
    }
    SetVisibility(ESlateVisibility::Visible);
    return Super::RebuildWidget();
}
void USteelCityJoystick::UpdateInput(const FGeometry& Geometry, const FPointerEvent& Event)
{
    const FVector2D Size = Geometry.GetLocalSize();
    const double Radius = FMath::Max(1.0, FMath::Min(Size.X,Size.Y)*.5-24.0);
    FVector2D Delta = Geometry.AbsoluteToLocal(Event.GetScreenSpacePosition())-Size*.5f;
    const double Length = Delta.Size();
    if (Length > Radius) Delta *= Radius/Length;
    Input = Delta/Radius;
    if (Input.Size() < .08f) Input = FVector2D::ZeroVector;
    if (ThumbSlot) ThumbSlot->SetPosition(Input*Radius);
}
FReply USteelCityJoystick::NativeOnTouchStarted(const FGeometry& Geometry,const FPointerEvent& Event)
{
    if (ActivePointer != INDEX_NONE) return FReply::Unhandled();
    ActivePointer = Event.GetPointerIndex(); ActiveUser = Event.GetUserIndex();
    UpdateInput(Geometry,Event);
    return FReply::Handled().CaptureMouse(TakeWidget());
}
FReply USteelCityJoystick::NativeOnTouchMoved(const FGeometry& Geometry,const FPointerEvent& Event)
{
    if (ActivePointer != Event.GetPointerIndex() || ActiveUser != Event.GetUserIndex()) return FReply::Unhandled();
    UpdateInput(Geometry,Event);
    return FReply::Handled();
}
FReply USteelCityJoystick::NativeOnTouchEnded(const FGeometry&,const FPointerEvent& Event)
{
    if (ActivePointer != Event.GetPointerIndex() || ActiveUser != Event.GetUserIndex()) return FReply::Unhandled();
    ResetInput();
    return FReply::Handled().ReleaseMouseCapture();
}
void USteelCityJoystick::ResetInput()
{
    ActivePointer = INDEX_NONE; ActiveUser = INDEX_NONE; Input = FVector2D::ZeroVector;
    if (ThumbSlot) ThumbSlot->SetPosition(FVector2D::ZeroVector);
}
void USteelCityJoystick::NativeOnMouseCaptureLost(const FCaptureLostEvent& Event)
{
    ResetInput(); Super::NativeOnMouseCaptureLost(Event);
}
void USteelCityJoystick::NativeDestruct()
{
    ResetInput(); Super::NativeDestruct();
}
