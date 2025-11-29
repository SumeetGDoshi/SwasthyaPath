/**
 * Tests for API client
 * Plan: /Users/sums/mcpDocs/plans/2025-11-27-write-comprehensive-test-cases-for-the-swasthyapat.md
 * Phase 3: Frontend API Client Tests
 */

import {
  ApiError,
  checkHealth,
  uploadReport,
  updateDuplicateDecision,
  getReports,
  getReport,
  getTimeline,
  getSavings,
  setupDemo,
  getDemoUser,
  loadUserData,
} from '@/lib/api'

// Mock fetch globally
const mockFetch = jest.fn()
global.fetch = mockFetch

beforeEach(() => {
  mockFetch.mockClear()
})

describe('ApiError', () => {
  it('should create error with message and status', () => {
    const error = new ApiError('Not found', 404)
    expect(error.message).toBe('Not found')
    expect(error.status).toBe(404)
    expect(error.name).toBe('ApiError')
  })

  it('should be instance of Error', () => {
    const error = new ApiError('Test error', 500)
    expect(error).toBeInstanceOf(Error)
  })

  it('should have correct stack trace', () => {
    const error = new ApiError('Stack test', 400)
    expect(error.stack).toBeDefined()
  })
})

describe('checkHealth', () => {
  it('should call health endpoint', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ 
        status: 'healthy', 
        version: '1.0.0',
        timestamp: '2024-11-15T10:00:00Z'
      }),
    })

    const result = await checkHealth()
    
    expect(result.status).toBe('healthy')
    expect(result.version).toBe('1.0.0')
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/health'),
      expect.any(Object)
    )
  })

  it('should throw ApiError on failure', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: () => Promise.resolve({ error: 'Server error' }),
    })

    await expect(checkHealth()).rejects.toThrow(ApiError)
    await expect(checkHealth()).rejects.toThrow('Server error')
  })

  it('should handle network errors', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'))
    
    await expect(checkHealth()).rejects.toThrow()
  })
})

describe('uploadReport', () => {
  it('should upload file with form data', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        success: true,
        report_id: 'test-123',
        extracted_data: { tests: [] },
        duplicate_alerts: [],
        message: 'Report analyzed',
        total_potential_savings: 0,
      }),
    })

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    const result = await uploadReport(file, 'user-123')

    expect(result.success).toBe(true)
    expect(result.report_id).toBe('test-123')
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/upload-report'),
      expect.objectContaining({ method: 'POST' })
    )
  })

  it('should include context when provided', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        success: true,
        report_id: 'test-456',
        duplicate_alerts: [],
      }),
    })

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    await uploadReport(file, 'user-123', 'Patient has diabetes')

    // Verify FormData was created with context
    const callArgs = mockFetch.mock.calls[0]
    expect(callArgs[1].body).toBeInstanceOf(FormData)
  })

  it('should handle upload errors', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: () => Promise.resolve({ error: 'Invalid file type' }),
    })

    const file = new File(['test'], 'test.txt', { type: 'text/plain' })
    await expect(uploadReport(file, 'user-123')).rejects.toThrow(ApiError)
  })

  it('should handle server errors', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: () => Promise.resolve({ error: 'Processing failed' }),
    })

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    await expect(uploadReport(file, 'user-123')).rejects.toThrow(ApiError)
  })
})

describe('updateDuplicateDecision', () => {
  it('should update decision to skip', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        success: true,
        alert_id: 'alert-123',
        decision: 'skip',
        message: 'Decision recorded',
      }),
    })

    const result = await updateDuplicateDecision('alert-123', 'skip')
    
    expect(result.decision).toBe('skip')
    expect(result.success).toBe(true)
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/duplicate-decision/alert-123'),
      expect.objectContaining({ method: 'POST' })
    )
  })

  it('should update decision to proceed', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        success: true,
        alert_id: 'alert-456',
        decision: 'proceed',
        message: 'Decision recorded',
      }),
    })

    const result = await updateDuplicateDecision('alert-456', 'proceed')
    expect(result.decision).toBe('proceed')
  })

  it('should handle not found error', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: () => Promise.resolve({ error: 'Alert not found' }),
    })

    await expect(updateDuplicateDecision('invalid', 'skip')).rejects.toThrow(ApiError)
  })
})

describe('getReports', () => {
  it('should fetch user reports', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        user_id: 'user-123',
        reports: [
          { id: '1', report_type: 'lab_test' },
          { id: '2', report_type: 'imaging' },
        ],
        total_count: 2,
      }),
    })

    const result = await getReports('user-123')
    
    expect(result.user_id).toBe('user-123')
    expect(result.reports).toHaveLength(2)
    expect(result.total_count).toBe(2)
  })

  it('should handle empty reports', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        user_id: 'user-123',
        reports: [],
        total_count: 0,
      }),
    })

    const result = await getReports('user-123')
    expect(result.reports).toHaveLength(0)
  })
})

describe('getReport', () => {
  it('should fetch specific report', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        id: 'report-123',
        user_id: 'user-456',
        report_type: 'lab_test',
        report_date: '2024-11-15',
      }),
    })

    const result = await getReport('report-123')
    
    expect(result.id).toBe('report-123')
    expect(result.report_type).toBe('lab_test')
  })

  it('should handle report not found', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: () => Promise.resolve({ error: 'Report not found' }),
    })

    await expect(getReport('invalid-id')).rejects.toThrow(ApiError)
  })
})

describe('getTimeline', () => {
  it('should fetch timeline entries', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        user_id: 'user-123',
        entries: [
          { id: '1', test_name: 'HbA1c', status: 'normal' },
          { id: '2', test_name: 'CBC', status: 'abnormal' },
        ],
        total_tests: 2,
      }),
    })

    const result = await getTimeline('user-123')
    
    expect(result.entries).toHaveLength(2)
    expect(result.total_tests).toBe(2)
  })

  it('should handle empty timeline', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        user_id: 'user-123',
        entries: [],
        total_tests: 0,
      }),
    })

    const result = await getTimeline('user-123')
    expect(result.total_tests).toBe(0)
  })
})

describe('getSavings', () => {
  it('should fetch savings summary', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        user_id: 'user-123',
        total_savings: 2100,
        tests_skipped: 3,
        breakdown: [
          { test_name: 'HbA1c', date_skipped: '2024-11-15', amount_saved: 700 },
        ],
      }),
    })

    const result = await getSavings('user-123')
    
    expect(result.total_savings).toBe(2100)
    expect(result.tests_skipped).toBe(3)
    expect(result.breakdown).toHaveLength(1)
  })

  it('should handle zero savings', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        user_id: 'user-123',
        total_savings: 0,
        tests_skipped: 0,
        breakdown: [],
      }),
    })

    const result = await getSavings('user-123')
    expect(result.total_savings).toBe(0)
  })
})

describe('setupDemo', () => {
  it('should setup demo data', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        success: true,
        user_id: 'demo-user-123',
        message: 'Demo data created successfully',
        reports_created: 4,
      }),
    })

    const result = await setupDemo()
    
    expect(result.success).toBe(true)
    expect(result.user_id).toBe('demo-user-123')
    expect(result.reports_created).toBe(4)
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/demo/setup'),
      expect.objectContaining({ method: 'POST' })
    )
  })

  it('should handle existing demo user', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        success: true,
        user_id: 'demo-user-123',
        message: 'Demo user already exists',
        reports_created: 0,
      }),
    })

    const result = await setupDemo()
    expect(result.reports_created).toBe(0)
  })
})

describe('getDemoUser', () => {
  it('should fetch demo user info', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        user_id: 'demo-user-123',
        name: 'Rahul Kumar',
        age: 42,
        gender: 'Male',
      }),
    })

    const result = await getDemoUser()
    
    expect(result.user_id).toBe('demo-user-123')
    expect(result.name).toBe('Rahul Kumar')
    expect(result.age).toBe(42)
  })
})

describe('loadUserData', () => {
  it('should load all user data in parallel', async () => {
    // Mock all three endpoints
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          user_id: 'user-123',
          entries: [],
          total_tests: 0,
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          user_id: 'user-123',
          total_savings: 1000,
          tests_skipped: 2,
          breakdown: [],
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          user_id: 'user-123',
          reports: [],
          total_count: 0,
        }),
      })

    const result = await loadUserData('user-123')
    
    expect(result.timeline).toBeDefined()
    expect(result.savings).toBeDefined()
    expect(result.reports).toBeDefined()
    expect(mockFetch).toHaveBeenCalledTimes(3)
  })

  it('should fail if any request fails', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ entries: [], total_tests: 0 }),
      })
      .mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ error: 'Server error' }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ reports: [], total_count: 0 }),
      })

    await expect(loadUserData('user-123')).rejects.toThrow()
  })
})

describe('Error handling', () => {
  it('should handle JSON parse errors gracefully', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: () => Promise.reject(new Error('Invalid JSON')),
    })

    await expect(checkHealth()).rejects.toThrow('Internal Server Error')
  })

  it('should include status in ApiError', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 403,
      json: () => Promise.resolve({ error: 'Forbidden' }),
    })

    try {
      await checkHealth()
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError)
      expect((error as ApiError).status).toBe(403)
    }
  })
})


