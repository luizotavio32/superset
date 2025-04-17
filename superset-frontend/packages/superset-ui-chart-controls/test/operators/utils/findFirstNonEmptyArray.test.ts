/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
import { findFirstNonEmptyArray } from '@superset-ui/chart-controls';

describe('findFirstNonEmptyArray', () => {
  test('returns empty array if no arguments provided', () => {
    // @ts-ignore
    expect(findFirstNonEmptyArray()).toEqual([]);
  });

  test('returns empty array if all provided arrays are empty or undefined', () => {
    expect(findFirstNonEmptyArray([], undefined, [])).toEqual([]);
  });

  test('returns the first non-empty array when it is the first argument', () => {
    const nonEmpty = ['a'];
    expect(findFirstNonEmptyArray(nonEmpty, ['b'])).toEqual(nonEmpty);
  });

  test('returns the first non-empty array when the first argument is empty', () => {
    const nonEmpty = ['foo'];
    expect(findFirstNonEmptyArray([], nonEmpty, ['bar'])).toEqual(nonEmpty);
  });

  test('handles multiple empty arrays before a non-empty array', () => {
    const nonEmpty = ['value'];
    expect(findFirstNonEmptyArray([], undefined, [], nonEmpty, ['another'])).toEqual(nonEmpty);
  });
});