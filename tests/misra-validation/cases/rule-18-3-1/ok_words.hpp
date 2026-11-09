// Near miss: the words, not the constructs.
#ifndef KV_RULE_18_3_1_OK_WORDS_HPP
#define KV_RULE_18_3_1_OK_WORDS_HPP

#include <cstdint>

namespace kv::rule_18_3_1::ok_words {

constexpr const char* kLog = "throw, try and catch are not used here";

struct Retry {
  std::uint8_t throttle = 0U;
  std::uint8_t catch_up = 0U;
};

[[nodiscard]] inline bool retry(const Retry& r) { return (r.throttle > 0U) && (kLog != nullptr); }

}  // namespace kv::rule_18_3_1::ok_words

#endif  // KV_RULE_18_3_1_OK_WORDS_HPP
