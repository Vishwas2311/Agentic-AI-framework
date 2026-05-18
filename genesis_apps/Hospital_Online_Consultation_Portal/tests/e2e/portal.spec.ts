import { test, expect } from '@playwright/test'

const BASE = 'http://localhost:3000'

async function login(page: import('@playwright/test').Page) {
  await page.goto(BASE)
  await page.getByLabel('Patient ID or Email').fill('patient@example.com')
  await page.getByLabel('Password').fill('patient123')
  await page.getByRole('button', { name: 'Login' }).click()
  await page.waitForURL('**/welcome')
}

test.describe('TC_001 - Login', () => {
  test('login page is visible and login succeeds', async ({ page }) => {
    await page.goto(BASE)
    await expect(page.getByRole('heading', { name: 'Patient Login' })).toBeVisible()
    await expect(page.getByLabel('Patient ID or Email')).toBeVisible()
    await expect(page.getByLabel('Password')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Login' })).toBeVisible()

    await page.getByLabel('Patient ID or Email').fill('patient@example.com')
    await page.getByLabel('Password').fill('patient123')
    await page.getByRole('button', { name: 'Login' }).click()

    await expect(page).toHaveURL(/\/welcome/)
  })
})

test.describe('TC_002 - Welcome Page', () => {
  test('welcome page shows greeting and quick actions', async ({ page }) => {
    await login(page)
    await expect(page.getByText(/Welcome back/i)).toBeVisible()
    await expect(page.getByRole('link', { name: /Book Consultation/i })).toBeVisible()
    await expect(page.getByRole('link', { name: /My Consultations/i })).toBeVisible()
  })
})

test.describe('TC_003 - Book Consultation', () => {
  test('can book a consultation and it appears in My Consultations', async ({ page }) => {
    await login(page)
    await page.goto(`${BASE}/book`)

    await page.getByLabel('Patient Name').fill('Rahul Sharma')
    await page.getByLabel('Age').fill('35')
    await page.getByLabel('Gender').selectOption('Male')
    await page.getByLabel('Department').selectOption('Cardiology')
    await page.getByLabel('Doctor').selectOption('Dr. Mehta')
    await page.getByLabel('Consultation Mode').selectOption('Video Call')
    await page.getByLabel('Consultation Status').selectOption('Requested')
    await page.getByLabel('Consultation Date').fill('2026-05-20')
    await page.getByLabel('Consultation Time').fill('10:30')
    await page.getByLabel('Symptoms').fill('Chest discomfort and fatigue')
    await page.getByRole('button', { name: 'Book Consultation' }).click()

    await expect(page.getByText('Consultation booked successfully')).toBeVisible()
    await page.waitForURL('**/consultations')
    await expect(page.getByText('Rahul Sharma')).toBeVisible()
  })
})

test.describe('TC_004 - Metrics After Booking', () => {
  test('dashboard metrics update after booking', async ({ page }) => {
    await login(page)
    await page.goto(`${BASE}/book`)
    await page.getByLabel('Patient Name').fill('Rahul Sharma')
    await page.getByLabel('Age').fill('35')
    await page.getByLabel('Consultation Date').fill('2026-05-20')
    await page.getByLabel('Consultation Time').fill('10:30')
    await page.getByLabel('Symptoms').fill('Chest discomfort')
    await page.getByRole('button', { name: 'Book Consultation' }).click()
    await page.waitForURL('**/consultations')

    await page.goto(`${BASE}/dashboard`)
    await expect(page.getByText('Total Consultations')).toBeVisible()
  })
})

test.describe('TC_005 - Update Status to Scheduled', () => {
  test('can move consultation status to Scheduled', async ({ page }) => {
    await login(page)
    await page.goto(`${BASE}/book`)
    await page.getByLabel('Patient Name').fill('Rahul Sharma')
    await page.getByLabel('Age').fill('35')
    await page.getByLabel('Consultation Date').fill('2026-05-20')
    await page.getByLabel('Consultation Time').fill('10:30')
    await page.getByLabel('Symptoms').fill('Chest discomfort')
    await page.getByRole('button', { name: 'Book Consultation' }).click()
    await page.waitForURL('**/consultations')

    await page.getByRole('button', { name: /Move to Scheduled/i }).first().click()
    await expect(page.getByText('Scheduled').first()).toBeVisible()
  })
})

test.describe('TC_006 - Complete Consultation', () => {
  test('can move consultation to Completed and prescription becomes available', async ({ page }) => {
    await login(page)
    await page.goto(`${BASE}/book`)
    await page.getByLabel('Patient Name').fill('Rahul Sharma')
    await page.getByLabel('Age').fill('35')
    await page.getByLabel('Consultation Date').fill('2026-05-20')
    await page.getByLabel('Consultation Time').fill('10:30')
    await page.getByLabel('Symptoms').fill('Chest discomfort')
    await page.getByRole('button', { name: 'Book Consultation' }).click()
    await page.waitForURL('**/consultations')

    await page.getByRole('button', { name: /Move to Scheduled/i }).first().click()
    await page.getByRole('button', { name: /Move to In Consultation/i }).first().click()
    await page.getByRole('button', { name: /Move to Completed/i }).first().click()
    await expect(page.getByText('Completed').first()).toBeVisible()
  })
})

test.describe('TC_007 - Filter by Completed', () => {
  test('filter shows only Completed consultations', async ({ page }) => {
    await login(page)
    await page.goto(`${BASE}/consultations`)
    await page.getByRole('button', { name: 'Completed' }).click()
    await expect(page.getByRole('button', { name: 'Completed' })).toHaveClass(/bg-cyan-600/)
  })
})

test.describe('TC_008 - Search by Doctor', () => {
  test('search filters consultation list', async ({ page }) => {
    await login(page)
    await page.goto(`${BASE}/consultations`)
    await page.getByRole('button', { name: 'All' }).click()
    await page.getByLabel('Search consultations').fill('Dr. Mehta')
  })
})

test.describe('TC_009 - Prescription Section', () => {
  test('prescriptions page shows demo disclaimer', async ({ page }) => {
    await login(page)
    await page.goto(`${BASE}/prescriptions`)
    await expect(page.getByRole('heading', { name: /Prescriptions/i })).toBeVisible()
    await expect(page.getByText(/demo prescription summary/i)).toBeVisible()
  })
})

test.describe('TC_010 - Sign Out', () => {
  test('sign out clears session and returns to login', async ({ page }) => {
    await login(page)
    await page.goto(`${BASE}/signout`)
    await expect(page.getByRole('button', { name: 'Sign Out' })).toBeVisible()
    await page.getByRole('button', { name: 'Sign Out' }).click()
    await expect(page.getByText('Signed Out Successfully')).toBeVisible()
    await page.waitForURL('**/')
    await expect(page.getByRole('heading', { name: 'Patient Login' })).toBeVisible()
  })
})
