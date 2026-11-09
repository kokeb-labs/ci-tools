// Near misses (near): one call, or one call and a member access, in the range initializer.
#ifndef KV_RULE_9_5_2_OK_NEAR_HPP
#define KV_RULE_9_5_2_OK_NEAR_HPP

#include <array>
#include <cstdint>

namespace kv::rule_9_5_2::ok_near {

struct Table {
  std::array<std::uint32_t, 3> data{};
};

inline constexpr Table kTable{{1U, 2U, 3U}};

inline const Table& table() { return kTable; }

inline std::uint32_t any() {
  std::uint32_t acc = 0U;
  for (const std::uint32_t v : table().data) {
    acc = acc | v;
  }
  return acc;
}

}  // namespace kv::rule_9_5_2::ok_near

#endif  // KV_RULE_9_5_2_OK_NEAR_HPP
