// Near miss: an untyped unscoped enumerator transferred to an integer type wide enough for its values.
#ifndef KV_RULE_10_2_3_OK_TRANSFER_HPP
#define KV_RULE_10_2_3_OK_TRANSFER_HPP

#include <cstdint>

namespace kv::rule_10_2_3::ok_transfer {

enum Plain { kOff, kOn };

[[nodiscard]] inline std::int32_t widen(std::int32_t v) { return v; }

[[nodiscard]] inline std::int32_t as_int(Plain p) {
  const std::int32_t i = p;
  return widen(i);
}

}  // namespace kv::rule_10_2_3::ok_transfer

#endif  // KV_RULE_10_2_3_OK_TRANSFER_HPP
