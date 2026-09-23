#!/usr/bin/env python3
"""
Standalone test script for AstronomyComputationalService improvements
"""

import sys
import os
import asyncio
import numpy as np

# Mock BaseService and other dependencies
class MockBaseService:
    def __init__(self, service_name=None):
        self.service_name = service_name or "MockService"
    
    def log_request(self, request_data):
        pass
    
    def handle_error(self, error, context):
        return {"error": str(error), "context": context}

# Mock logger
class MockLogger:
    def info(self, msg):
        print(f"INFO: {msg}")
    
    def error(self, msg):
        print(f"ERROR: {msg}")
    
    def warning(self, msg):
        print(f"WARNING: {msg}")

# Mock the problematic imports
sys.modules['app.services.base_service'] = type('MockModule', (), {'BaseService': MockBaseService})()
sys.modules['app.core.bootstrap_logging'] = type('MockModule', (), {'logger': MockLogger()})()

# Now import the astronomy service code directly
exec(open('app/services/astronomy_computational_service.py').read())

async def test_astronomy_improvements():
    """Test the improved AstronomyComputationalService"""
    print("🌟 Testing AstronomyComputationalService Improvements (Standalone)")
    print("=" * 70)
    
    try:
        # Create service instance
        service = AstronomyComputationalService()
        
        print(f"✅ Service created successfully")
        print(f"📊 Version: {service.version}")
        print(f"🔧 Advanced config: {len(service.advanced_config)} parameters")
        print(f"🤖 ML Available: {ML_AVAILABLE}")
        print(f"📊 SciPy Available: {SCIPY_AVAILABLE}")
        
        # Test 1: Service Info
        print("\n📋 Testing Service Info...")
        info_result = await service.process_request({"operation": "info"})
        print(f"✅ Service info retrieved")
        print(f"   Capabilities: {len(info_result['capabilities'])}")
        for cap in info_result['capabilities']:
            print(f"     - {cap}")
        print(f"   ML Available: {info_result['ml_available']}")
        print(f"   SciPy Available: {info_result['scipy_available']}")
        
        # Generate synthetic light curve data
        def generate_synthetic_light_curve(n_points=300, has_transit=True, transit_period=10.0, transit_depth=0.01):
            """Generate synthetic light curve with or without transit"""
            times = np.linspace(0, 50, n_points)  # 50 days of observations
            
            # Base stellar flux with some noise
            flux = np.ones_like(times) + np.random.normal(0, 0.001, len(times))
            
            if has_transit:
                # Add periodic transits
                transit_duration = 0.2  # days
                for i in range(len(times)):
                    phase = (times[i] % transit_period) / transit_period
                    if phase < transit_duration / transit_period or phase > (1 - transit_duration / transit_period):
                        flux[i] -= transit_depth
            
            # Add some stellar variability
            flux += 0.005 * np.sin(2 * np.pi * times / 25.0)  # 25-day rotation period
            
            return [{"time": float(t), "flux": float(f)} for t, f in zip(times, flux)]
        
        # Test 2: Advanced Exoplanet Detection
        print("\n🪐 Testing Advanced Exoplanet Detection...")
        
        # Generate test data with transit
        light_curve_with_transit = generate_synthetic_light_curve(n_points=200, has_transit=True)
        stellar_params = {
            "mass": 1.0,
            "radius": 1.0,
            "temperature": 5778,
            "metallicity": 0.0,
            "age": 4.6
        }
        
        detection_result = await service.advanced_exoplanet_detection(
            light_curve_with_transit, 
            stellar_params, 
            use_ml=True
        )
        
        if detection_result.get('success', False):
            print(f"✅ Advanced exoplanet detection successful")
            print(f"   Data points analyzed: {detection_result['data_points']}")
            algorithms = detection_result['algorithms_used']
            print(f"   Algorithms used:")
            for alg, success in algorithms.items():
                status = "✅" if success else "❌"
                print(f"     {status} {alg}")
            
            candidates = detection_result.get('transit_candidates', [])
            print(f"   Transit candidates found: {len(candidates)}")
            
            for i, candidate in enumerate(candidates[:2]):  # Show first 2
                print(f"     Candidate {i+1}:")
                print(f"       Period: {candidate['period']:.2f} days")
                print(f"       Depth: {candidate['depth']*1e6:.1f} ppm")
                print(f"       Duration: {candidate['duration']:.2f} hours")
                print(f"       Method: {candidate['method']}")
                print(f"       Confidence: {candidate['confidence']:.3f}")
            
            # Show detection statistics
            stats = detection_result.get('detection_statistics', {})
            print(f"   Detection statistics:")
            print(f"     Total: {stats.get('total_candidates', 0)}")
            print(f"     High confidence: {stats.get('high_confidence', 0)}")
            print(f"     Medium confidence: {stats.get('medium_confidence', 0)}")
        else:
            print(f"❌ Advanced detection failed: {detection_result.get('error', 'Unknown error')}")
        
        # Test 3: Realistic Gravitational Lensing
        print("\n🔭 Testing Realistic Gravitational Lensing...")
        
        lensing_result = await service.realistic_gravitational_lensing(
            lens_mass=1e11,      # Solar masses
            source_distance=8000, # parsecs
            lens_distance=4000,   # parsecs
            source_position=(0.1, 0.05)  # arcsec offset
        )
        
        if lensing_result.get('success', False):
            print(f"✅ Gravitational lensing simulation successful")
            print(f"   Einstein radius: {lensing_result['einstein_radius_arcsec']:.4f} arcsec")
            print(f"   Einstein radius: {lensing_result['einstein_radius_mas']:.1f} mas")
            print(f"   Total magnification: {lensing_result['total_magnification']:.2f}")
            
            # Show light curve
            light_curve = lensing_result.get('light_curve', [])
            print(f"   Light curve points: {len(light_curve)}")
            if light_curve:
                max_mag = max(mag for time, mag in light_curve)
                print(f"   Maximum magnification: {max_mag:.2f}")
            
            # Show relativistic effects
            rel_effects = lensing_result.get('relativistic_effects', {})
            if rel_effects and 'error' not in rel_effects:
                print(f"   Relativistic effects:")
                print(f"     Schwarzschild radius: {rel_effects.get('schwarzschild_radius_km', 0):.2f} km")
                print(f"     Post-Newtonian effects: {rel_effects.get('post_newtonian_effects', 'N/A')}")
        else:
            print(f"❌ Gravitational lensing failed: {lensing_result.get('error', 'Unknown error')}")
        
        # Test 4: Stellar Variability Analysis
        print("\n⭐ Testing Stellar Variability Analysis...")
        
        # Generate variable star light curve
        variable_light_curve = generate_synthetic_light_curve(n_points=250, has_transit=False)
        # Add stronger variability
        times = [p['time'] for p in variable_light_curve]
        for i, p in enumerate(variable_light_curve):
            # Add pulsation
            p['flux'] += 0.02 * np.sin(2 * np.pi * times[i] / 2.5)  # 2.5 day pulsation
            # Add rotation modulation
            p['flux'] += 0.01 * np.sin(2 * np.pi * times[i] / 15.0)  # 15 day rotation
        
        variability_result = await service.analyze_stellar_variability(
            variable_light_curve,
            analysis_type="comprehensive"
        )
        
        if variability_result.get('success', False):
            print(f"✅ Stellar variability analysis successful")
            print(f"   Analysis type: {variability_result['analysis_type']}")
            
            # Basic statistics
            basic_stats = variability_result.get('basic_statistics', {})
            if 'error' not in basic_stats:
                print(f"   Basic statistics:")
                print(f"     Coefficient of variation: {basic_stats.get('coefficient_of_variation', 0):.4f}")
                print(f"     Amplitude: {basic_stats.get('amplitude_percent', 0):.2f}%")
                print(f"     Is variable: {basic_stats.get('is_variable', False)}")
            
            # Period analysis
            period_analysis = variability_result.get('period_analysis', {})
            if period_analysis.get('success', False):
                dominant_period = period_analysis.get('dominant_period')
                if dominant_period:
                    print(f"   Period analysis:")
                    print(f"     Dominant period: {dominant_period['period_days']:.2f} days")
                    print(f"     Method: {period_analysis.get('method', 'unknown')}")
            
            # Variability classification
            var_class = variability_result.get('variability_classification', {})
            print(f"   Variability classification:")
            print(f"     Type: {var_class.get('type', 'unknown')}")
            print(f"     Confidence: {var_class.get('confidence', 0):.3f}")
            
            # Data quality
            data_quality = variability_result.get('data_quality', {})
            print(f"   Data quality:")
            print(f"     Data points: {data_quality.get('data_points', 0)}")
            print(f"     Time span: {data_quality.get('time_span_days', 0):.1f} days")
        else:
            print(f"❌ Stellar variability analysis failed: {variability_result.get('error', 'Unknown error')}")
        
        # Test 5: False Positive Detection
        print("\n🔍 Testing False Positive Detection...")
        
        # Create some test transit candidates
        test_candidates = [
            {
                "period": 10.5,
                "depth": 0.001,
                "duration": 3.2,
                "significance": 8.5,
                "method": "bls"
            },
            {
                "period": 2.1,
                "depth": 0.05,
                "duration": 8.0,
                "significance": 12.0,
                "method": "tls"
            }
        ]
        
        fp_result = await service.detect_false_positives(test_candidates, stellar_params)
        
        if fp_result.get('success', False):
            print(f"✅ False positive detection successful")
            
            summary = fp_result.get('summary', {})
            print(f"   Summary:")
            print(f"     Total candidates: {summary.get('total_candidates', 0)}")
            print(f"     Likely planets: {summary.get('likely_planets', 0)}")
            print(f"     Validation rate: {summary.get('validation_rate', 0):.1%}")
            
            candidates = fp_result.get('candidates', [])
            for candidate in candidates:
                print(f"   Candidate {candidate['candidate_id']}:")
                print(f"     Period: {candidate['period_days']:.1f} days")
                print(f"     Likely planet: {candidate['likely_planet']}")
                print(f"     Confidence: {candidate['confidence']:.3f}")
        else:
            print(f"❌ False positive detection failed: {fp_result.get('error', 'Unknown error')}")
        
        # Test 6: Legacy Support
        print("\n🔄 Testing Legacy Transit Analysis...")
        
        legacy_result = await service.process_request({
            "operation": "exoplanet_transit",
            "light_curve": light_curve_with_transit[:50]  # Smaller dataset
        })
        
        if legacy_result.get('success', False):
            print(f"✅ Legacy transit analysis successful")
            print(f"   Method: {legacy_result['method']}")
            print(f"   Estimated depth: {legacy_result['estimated_depth']:.5f}")
        else:
            print(f"❌ Legacy analysis failed: {legacy_result.get('error', 'Unknown error')}")
        
        print("\n🎉 Astronomy Computational Service Improvements Test Complete!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to run async test"""
    return asyncio.run(test_astronomy_improvements())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
