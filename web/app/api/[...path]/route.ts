export const maxDuration = 60

import { NextRequest, NextResponse } from 'next/server'

const BACKEND = process.env.AI_SERVICE_URL || (process.env.NODE_ENV === 'production' ? '' : 'http://127.0.0.1:8123')

async function forward(req: NextRequest, path: string[]) {
  if (!BACKEND) {
    return NextResponse.json(
      { detail: 'LearnLens backend is not configured. Set AI_SERVICE_URL in the project\'s environment variables.' },
      { status: 503 },
    )
  }
  const url = new URL(req.url)
  const target = `${BACKEND.replace(/\/$/, '')}/${path.join('/')}${url.search ? url.search : ''}`
  const headers = new Headers()
  const contentType = req.headers.get('content-type')
  if (contentType) headers.set('content-type', contentType)
  const teacherKey = req.headers.get('x-teacher-key')
  if (teacherKey) headers.set('x-teacher-key', teacherKey)
  const forwardedFor = req.headers.get('x-forwarded-for')
  if (forwardedFor) headers.set('x-forwarded-for', forwardedFor)
  const authorization = req.headers.get('authorization')
  if (authorization) headers.set('authorization', authorization)
  const init: RequestInit = { method: req.method, headers, cache: 'no-store' }
  if (!['GET', 'HEAD'].includes(req.method)) init.body = await req.arrayBuffer()
  const response = await fetch(target, init)
  const outHeaders = new Headers()
  outHeaders.set('content-type', response.headers.get('content-type') || 'application/json')
  return new NextResponse(response.body, { status: response.status, headers: outHeaders })
}

export async function GET(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return forward(req, (await ctx.params).path)
}
export async function POST(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return forward(req, (await ctx.params).path)
}
