# Copyright 2018 The JAX Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from functools import partial

import numpy as np

from jax._src import ad_util
from jax._src import core
from jax._src import dtypes

from jax._src import traceback_util
traceback_util.register_exclusion(__file__)

UnshapedArray = core.UnshapedArray
ShapedArray = core.ShapedArray
ConcreteArray = core.ConcreteArray
AbstractToken = core.AbstractToken
abstract_token = core.abstract_token
canonicalize_shape = core.canonicalize_shape
raise_to_shaped = core.raise_to_shaped

def zeros_like_array(x):
  dtype, weak_type = dtypes._lattice_result_type(x)
  dtype = dtypes.canonicalize_dtype(dtype)
  aval = ShapedArray(np.shape(x), dtype, weak_type=weak_type)
  return ad_util.zeros_like_aval(aval)

numpy_scalar_types = {
    np.int8, np.int16, np.int32, np.int64,
    np.uint8, np.uint16, np.uint32, np.uint64,
    dtypes.bfloat16, np.float16, np.float32, np.float64,
    np.complex64, np.complex128,
    np.bool_, np.longlong, np.intc,
}

array_types = {np.ndarray} | numpy_scalar_types

def canonical_concrete_aval(val, weak_type=None):
  return ConcreteArray(dtypes.canonicalize_dtype(np.result_type(val)), val,
                       weak_type=weak_type)

for t in array_types:
  core.pytype_aval_mappings[t] = canonical_concrete_aval
  ad_util.jaxval_zeros_likers[t] = zeros_like_array

core.literalable_types.update(array_types)

def _zeros_like_python_scalar(t, x):
  dtype = dtypes.canonicalize_dtype(dtypes.python_scalar_dtypes[t])
  aval = core.ShapedArray((), dtype, weak_type=True)
  return ad_util.zeros_like_aval(aval)

def _make_concrete_python_scalar(t, x):
  dtype = dtypes._scalar_type_to_dtype(t, x)
  return canonical_concrete_aval(np.array(x, dtype=dtype), weak_type=True)

for t in dtypes.python_scalar_dtypes:
  core.pytype_aval_mappings[t] = partial(_make_concrete_python_scalar, t)
  ad_util.jaxval_zeros_likers[t] = partial(_zeros_like_python_scalar, t)

core.literalable_types.update(dtypes.python_scalar_dtypes.keys())  # type: ignore
