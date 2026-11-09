// Near misses (near): bit_cast and a plain struct where a union would be tempting.
#ifndef KV_RULE_12_3_1_OK_NEAR_HPP
#define KV_RULE_12_3_1_OK_NEAR_HPP

#include <bit>
#include <cstdint>

namespace kv::rule_12_3_1::ok_near {

struct Value {
  bool is_int = true;
  std::uint32_t i = 0U;
  float f = 0.0F;
};

inline std::uint32_t bits(float v) { return std::bit_cast<std::uint32_t>(v); }

inline std::uint32_t as_int(const Value& v) { return v.is_int ? v.i : bits(v.f); }

}  // namespace kv::rule_12_3_1::ok_near

#endif  // KV_RULE_12_3_1_OK_NEAR_HPP
