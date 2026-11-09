// Near miss: # and ## in one macro, never on the same parameter.
#ifndef KV_RULE_19_3_2_OK_SPLIT_HPP
#define KV_RULE_19_3_2_OK_SPLIT_HPP

#include <cstdint>

#define KV_RULE_19_3_2_ENTRY(P, Q, R) {#P, Q##R}

namespace kv::rule_19_3_2_split::ok_split {

struct Entry {
  const char* name;
  std::uint32_t value;
};

constexpr std::uint32_t kAB = 3U;
constexpr Entry kEntry = KV_RULE_19_3_2_ENTRY(adc, kA, B);

[[nodiscard]] inline Entry entry() { return kEntry; }

[[nodiscard]] inline bool valid(const Entry& e) { return (e.name != nullptr) && (e.value == kAB); }

}  // namespace kv::rule_19_3_2_split::ok_split

#undef KV_RULE_19_3_2_ENTRY

#endif  // KV_RULE_19_3_2_OK_SPLIT_HPP
