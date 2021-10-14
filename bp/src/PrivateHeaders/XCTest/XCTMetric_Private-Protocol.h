//
//     Generated by class-dump 3.5 (64 bit) (Debug version compiled May 11 2021 09:30:43).
//
//  Copyright (C) 1997-2019 Steve Nygard.
//

#import <XCTest/XCTMetric-Protocol.h>

@class NSString, XCTMeasureOptions, XCTPerformanceMeasurementTimestamp;

@protocol XCTMetric_Private <XCTMetric>

@optional
@property(readonly, nonatomic) NSString *instrumentationName;
- (void)didStopMeasuringAtTimestamp:(XCTPerformanceMeasurementTimestamp *)arg1;
- (void)didStartMeasuringAtTimestamp:(XCTPerformanceMeasurementTimestamp *)arg1;
- (void)willBeginMeasuringAtEstimatedTimestamp:(XCTPerformanceMeasurementTimestamp *)arg1;
- (void)prepareToMeasureWithOptions:(XCTMeasureOptions *)arg1;
@end
