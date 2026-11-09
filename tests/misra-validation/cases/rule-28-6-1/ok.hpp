// Compliant: std::move is applied to a non-const named local that is not used again.
#ifndef KV_RULE_28_6_1_OK_HPP
#define KV_RULE_28_6_1_OK_HPP

#include <array>
#include <cstdint>
#include <utility>

namespace kv::rule_28_6_1::ok {

struct Buffer {
  std::array<std::uint8_t, 4U> data;
};

inline void take(Buffer& dest, Buffer source) { dest = std::move(source); }

}  // namespace kv::rule_28_6_1::ok

#endif  // KV_RULE_28_6_1_OK_HPP
