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
/* eslint-disable theme-colors/no-literal-colors */
import { SerializableThemeConfig } from './types';

const exampleThemes: Record<string, SerializableThemeConfig> = {
  superset: {
    token: {
      colorBgElevated: '#fafafa',
    },
  },
  supersetDark: {
    token: {},
    algorithm: 'dark',
  },
  supersetCompact: {
    token: {},
    algorithm: 'compact',
  },
  funky: {
    token: {
      colorPrimary: '#f759ab', // hot pink
      colorSuccess: '#52c41a',
      colorWarning: '#faad14',
      colorError: '#ff4d4f',
      colorInfo: '#40a9ff',
      borderRadius: 12,
      fontFamily: 'Comic Sans MS, cursive',
    },
    algorithm: 'default',
  },
  funkyDark: {
    token: {
      colorPrimary: '#f759ab', // hot pink
      colorSuccess: '#52c41a',
      colorWarning: '#faad14',
      colorError: '#ff4d4f',
      colorInfo: '#40a9ff',
      borderRadius: 12,
      fontFamily: 'Comic Sans MS, cursive',
    },
    algorithm: 'dark',
  },
};
export default exampleThemes;
