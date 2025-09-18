import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../UI/Card';
import { Button } from '../UI/Button';
import { Input } from '../UI/Input';
import { Label } from '../UI/Label';
import { Alert, AlertDescription } from '../UI/Alert';
import { Loader2, Save, TrendingUp, TrendingDown, Minus } from 'lucide-react';

const ESGDataForm = ({ onSubmit, initialData = null, isLoading = false }) => {
  const [formData, setFormData] = useState({
    company_name: '',
    year: new Date().getFullYear(),
    scope1_emissions: '',
    scope2_emissions: '',
    scope3_emissions: '',
    water_consumption: '',
    waste_generated: '',
    energy_consumption: '',
    renewable_energy_percentage: '',
    employee_count: '',
    revenue: '',
    additional_metrics: {}
  });

  const [errors, setErrors] = useState({});
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    if (initialData) {
      setFormData({
        company_name: initialData.company_name || '',
        year: initialData.year || new Date().getFullYear(),
        scope1_emissions: initialData.scope1_emissions || '',
        scope2_emissions: initialData.scope2_emissions || '',
        scope3_emissions: initialData.scope3_emissions || '',
        water_consumption: initialData.water_consumption || '',
        waste_generated: initialData.waste_generated || '',
        energy_consumption: initialData.energy_consumption || '',
        renewable_energy_percentage: initialData.renewable_energy_percentage || '',
        employee_count: initialData.employee_count || '',
        revenue: initialData.revenue || '',
        additional_metrics: initialData.additional_metrics || {}
      });
    }
  }, [initialData]);

  const validateForm = () => {
    const newErrors = {};

    if (!formData.company_name.trim()) {
      newErrors.company_name = 'Company name is required';
    }

    if (!formData.year || formData.year < 2000 || formData.year > 2030) {
      newErrors.year = 'Please enter a valid year between 2000 and 2030';
    }

    // Validate numeric fields
    const numericFields = [
      'scope1_emissions', 'scope2_emissions', 'scope3_emissions',
      'water_consumption', 'waste_generated', 'energy_consumption',
      'employee_count', 'revenue'
    ];

    numericFields.forEach(field => {
      if (formData[field] && (isNaN(formData[field]) || parseFloat(formData[field]) < 0)) {
        newErrors[field] = 'Please enter a valid positive number';
      }
    });

    // Validate renewable energy percentage
    if (formData.renewable_energy_percentage && 
        (isNaN(formData.renewable_energy_percentage) || 
         parseFloat(formData.renewable_energy_percentage) < 0 || 
         parseFloat(formData.renewable_energy_percentage) > 100)) {
      newErrors.renewable_energy_percentage = 'Please enter a percentage between 0 and 100';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    // Convert string values to numbers where appropriate
    const processedData = {
      ...formData,
      scope1_emissions: formData.scope1_emissions ? parseFloat(formData.scope1_emissions) : null,
      scope2_emissions: formData.scope2_emissions ? parseFloat(formData.scope2_emissions) : null,
      scope3_emissions: formData.scope3_emissions ? parseFloat(formData.scope3_emissions) : null,
      water_consumption: formData.water_consumption ? parseFloat(formData.water_consumption) : null,
      waste_generated: formData.waste_generated ? parseFloat(formData.waste_generated) : null,
      energy_consumption: formData.energy_consumption ? parseFloat(formData.energy_consumption) : null,
      renewable_energy_percentage: formData.renewable_energy_percentage ? parseFloat(formData.renewable_energy_percentage) : null,
      employee_count: formData.employee_count ? parseInt(formData.employee_count) : null,
      revenue: formData.revenue ? parseFloat(formData.revenue) : null
    };

    onSubmit(processedData);
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }));
    }
  };

  const getFieldIcon = (field, value) => {
    if (!value) return <Minus className="h-4 w-4 text-gray-400" />;
    
    // For emissions and waste, lower is better
    const lowerIsBetter = ['scope1_emissions', 'scope2_emissions', 'scope3_emissions', 'waste_generated', 'water_consumption', 'energy_consumption'];
    
    if (lowerIsBetter.includes(field)) {
      return <TrendingDown className="h-4 w-4 text-green-500" />;
    } else {
      return <TrendingUp className="h-4 w-4 text-green-500" />;
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl font-bold text-gray-900">
          ESG Data Input
        </CardTitle>
        <p className="text-gray-600">
          Enter your company's ESG metrics to get personalized benchmarking and recommendations
        </p>
      </CardHeader>
      
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Label htmlFor="company_name">Company Name *</Label>
              <Input
                id="company_name"
                type="text"
                value={formData.company_name}
                onChange={(e) => handleInputChange('company_name', e.target.value)}
                placeholder="Enter your company name"
                className={errors.company_name ? 'border-red-500' : ''}
              />
              {errors.company_name && (
                <p className="text-red-500 text-sm mt-1">{errors.company_name}</p>
              )}
            </div>

            <div>
              <Label htmlFor="year">Reporting Year *</Label>
              <Input
                id="year"
                type="number"
                value={formData.year}
                onChange={(e) => handleInputChange('year', parseInt(e.target.value))}
                min="2000"
                max="2030"
                className={errors.year ? 'border-red-500' : ''}
              />
              {errors.year && (
                <p className="text-red-500 text-sm mt-1">{errors.year}</p>
              )}
            </div>
          </div>

          {/* Emissions Data */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">
              Greenhouse Gas Emissions (tCO2e)
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="scope1_emissions" className="flex items-center gap-2">
                  {getFieldIcon('scope1_emissions', formData.scope1_emissions)}
                  Scope 1 Emissions
                </Label>
                <Input
                  id="scope1_emissions"
                  type="number"
                  step="0.01"
                  value={formData.scope1_emissions}
                  onChange={(e) => handleInputChange('scope1_emissions', e.target.value)}
                  placeholder="Direct emissions"
                  className={errors.scope1_emissions ? 'border-red-500' : ''}
                />
                {errors.scope1_emissions && (
                  <p className="text-red-500 text-sm mt-1">{errors.scope1_emissions}</p>
                )}
              </div>

              <div>
                <Label htmlFor="scope2_emissions" className="flex items-center gap-2">
                  {getFieldIcon('scope2_emissions', formData.scope2_emissions)}
                  Scope 2 Emissions
                </Label>
                <Input
                  id="scope2_emissions"
                  type="number"
                  step="0.01"
                  value={formData.scope2_emissions}
                  onChange={(e) => handleInputChange('scope2_emissions', e.target.value)}
                  placeholder="Indirect emissions"
                  className={errors.scope2_emissions ? 'border-red-500' : ''}
                />
                {errors.scope2_emissions && (
                  <p className="text-red-500 text-sm mt-1">{errors.scope2_emissions}</p>
                )}
              </div>

              <div>
                <Label htmlFor="scope3_emissions" className="flex items-center gap-2">
                  {getFieldIcon('scope3_emissions', formData.scope3_emissions)}
                  Scope 3 Emissions
                </Label>
                <Input
                  id="scope3_emissions"
                  type="number"
                  step="0.01"
                  value={formData.scope3_emissions}
                  onChange={(e) => handleInputChange('scope3_emissions', e.target.value)}
                  placeholder="Value chain emissions"
                  className={errors.scope3_emissions ? 'border-red-500' : ''}
                />
                {errors.scope3_emissions && (
                  <p className="text-red-500 text-sm mt-1">{errors.scope3_emissions}</p>
                )}
              </div>
            </div>
          </div>

          {/* Resource Consumption */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">
              Resource Consumption
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="water_consumption" className="flex items-center gap-2">
                  {getFieldIcon('water_consumption', formData.water_consumption)}
                  Water Consumption (m³)
                </Label>
                <Input
                  id="water_consumption"
                  type="number"
                  step="0.01"
                  value={formData.water_consumption}
                  onChange={(e) => handleInputChange('water_consumption', e.target.value)}
                  placeholder="Total water usage"
                  className={errors.water_consumption ? 'border-red-500' : ''}
                />
                {errors.water_consumption && (
                  <p className="text-red-500 text-sm mt-1">{errors.water_consumption}</p>
                )}
              </div>

              <div>
                <Label htmlFor="waste_generated" className="flex items-center gap-2">
                  {getFieldIcon('waste_generated', formData.waste_generated)}
                  Waste Generated (tonnes)
                </Label>
                <Input
                  id="waste_generated"
                  type="number"
                  step="0.01"
                  value={formData.waste_generated}
                  onChange={(e) => handleInputChange('waste_generated', e.target.value)}
                  placeholder="Total waste produced"
                  className={errors.waste_generated ? 'border-red-500' : ''}
                />
                {errors.waste_generated && (
                  <p className="text-red-500 text-sm mt-1">{errors.waste_generated}</p>
                )}
              </div>

              <div>
                <Label htmlFor="energy_consumption" className="flex items-center gap-2">
                  {getFieldIcon('energy_consumption', formData.energy_consumption)}
                  Energy Consumption (MWh)
                </Label>
                <Input
                  id="energy_consumption"
                  type="number"
                  step="0.01"
                  value={formData.energy_consumption}
                  onChange={(e) => handleInputChange('energy_consumption', e.target.value)}
                  placeholder="Total energy usage"
                  className={errors.energy_consumption ? 'border-red-500' : ''}
                />
                {errors.energy_consumption && (
                  <p className="text-red-500 text-sm mt-1">{errors.energy_consumption}</p>
                )}
              </div>

              <div>
                <Label htmlFor="renewable_energy_percentage" className="flex items-center gap-2">
                  {getFieldIcon('renewable_energy_percentage', formData.renewable_energy_percentage)}
                  Renewable Energy (%)
                </Label>
                <Input
                  id="renewable_energy_percentage"
                  type="number"
                  step="0.1"
                  min="0"
                  max="100"
                  value={formData.renewable_energy_percentage}
                  onChange={(e) => handleInputChange('renewable_energy_percentage', e.target.value)}
                  placeholder="Percentage of renewable energy"
                  className={errors.renewable_energy_percentage ? 'border-red-500' : ''}
                />
                {errors.renewable_energy_percentage && (
                  <p className="text-red-500 text-sm mt-1">{errors.renewable_energy_percentage}</p>
                )}
              </div>
            </div>
          </div>

          {/* Company Information */}
          <div className="space-y-4">
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              {showAdvanced ? 'Hide' : 'Show'} Additional Information
            </button>

            {showAdvanced && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <Label htmlFor="employee_count">Employee Count</Label>
                  <Input
                    id="employee_count"
                    type="number"
                    value={formData.employee_count}
                    onChange={(e) => handleInputChange('employee_count', e.target.value)}
                    placeholder="Number of employees"
                    className={errors.employee_count ? 'border-red-500' : ''}
                  />
                  {errors.employee_count && (
                    <p className="text-red-500 text-sm mt-1">{errors.employee_count}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="revenue">Annual Revenue (USD)</Label>
                  <Input
                    id="revenue"
                    type="number"
                    step="0.01"
                    value={formData.revenue}
                    onChange={(e) => handleInputChange('revenue', e.target.value)}
                    placeholder="Annual revenue in USD"
                    className={errors.revenue ? 'border-red-500' : ''}
                  />
                  {errors.revenue && (
                    <p className="text-red-500 text-sm mt-1">{errors.revenue}</p>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-4 pt-6 border-t">
            <Button
              type="submit"
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Save ESG Data
                </>
              )}
            </Button>
          </div>
        </form>

        {/* Help Text */}
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h4 className="font-medium text-blue-900 mb-2">Need Help?</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Scope 1: Direct emissions from owned/controlled sources</li>
            <li>• Scope 2: Indirect emissions from purchased electricity</li>
            <li>• Scope 3: All other indirect emissions in the value chain</li>
            <li>• Enter data in the specified units for accurate benchmarking</li>
            <li>• Leave fields blank if data is not available</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
};

export default ESGDataForm;
