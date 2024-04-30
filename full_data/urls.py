from django.urls import path


from full_data.data_views import AllDataCatListAPIView, AllDataFilterByLatLongDistanceView, AllDataFilterView, ApproveRejectView, InvestorInfoOwnListView, InvestorInfoView
from full_data.data_views import CurrencyListView, FinancialDataAPIView, FinancialDataDraftRetrieveView, FinancialDataDraftView, FinancialDataView
from full_data.data_views import InformativeDataDraftRetrieveView, InformativeDataDraftView, InformativeDataView, ObjectPhotoView
from full_data.data_views import AreaAPIListView, AreaListView, CategoryApiListView, CategoryListView, CategoryRetrieveView, LocationView, MainDataAPIView, MainDataDraftListView, MainDataDraftRetrieveView, MainDataDraftView, MainDataView, ObjectPhotoViewList
from smartnote.views import SmartNoteCreateView, SmartNoteDestroyView, SmartNoteListView, SmartNoteRetrieveView, SmartNoteUpdateView

urlpatterns = [
    path('main-data-draft-save', MainDataDraftView.as_view()),
    path('main-data-create', MainDataView.as_view()),
    path('main-data-create-api', MainDataAPIView.as_view()),
    path('main-data-draft-get', MainDataDraftRetrieveView.as_view()),
    path('main-data-draft-get-api', MainDataDraftListView.as_view()),
    #path('main-data-approved-get', MainDataApprovedRetrieveView.as_view()),
    path('informative-data-draft-save', InformativeDataDraftView.as_view()),
    path('informative-data-create', InformativeDataView.as_view()),
    path('informative-data-draft-get', InformativeDataDraftRetrieveView.as_view()),
    #path('informative-data-approved-get', InformativeDataApprovedRetrieveView.as_view()),
    path('financial-data-draft-save', FinancialDataDraftView.as_view()),
    path('financial-data-create', FinancialDataView.as_view()),
    path('financial-data-create-api', FinancialDataAPIView.as_view()),
    path('financial-data-draft-get', FinancialDataDraftRetrieveView.as_view()),
    #path('financial-data-approved-get', FinancialDataApprovedRetrieveView.as_view()),
    path('object-photo', ObjectPhotoView.as_view()),
    path('object-photo-get', ObjectPhotoViewList.as_view()),
    #path('set-status-ready', SetReadyStatusView.as_view()),
    path('investor-info-create', InvestorInfoView.as_view()),
    path('category-list', CategoryListView.as_view()),
    path('category-list-api', CategoryApiListView.as_view()),
    path('category-list-api/<int:pk>', CategoryRetrieveView.as_view()),
    path('alldata-cat-list-api', AllDataCatListAPIView.as_view()),
    path('currency-list', CurrencyListView.as_view()),
    path('area-list', AreaListView.as_view()),
    path('area-list-api', AreaAPIListView.as_view()),
    path('location', LocationView.as_view()),
    path('approve-reject-investor', ApproveRejectView.as_view()),
    path('investor-info-own', InvestorInfoOwnListView.as_view()),
    path('all-data-filter', AllDataFilterView.as_view()),
    path('all-data-by-lat-long-distance-filter', AllDataFilterByLatLongDistanceView.as_view()),
    

    # smartnote
    path('smart-note-delete/<pk>', SmartNoteDestroyView.as_view()),
    path('smart-note-update/<pk>', SmartNoteUpdateView.as_view()),
    path('smart-note-get/<pk>', SmartNoteRetrieveView.as_view()),
    path('smart-note-create', SmartNoteCreateView.as_view()),
    path('smart-note-list', SmartNoteListView.as_view()),
]