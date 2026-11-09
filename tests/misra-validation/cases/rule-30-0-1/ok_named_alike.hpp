// Compliant near miss: a log sink of our own with members named print and puts.
#ifndef KV_RULE_30_0_1_OK_NAMED_ALIKE_HPP
#define KV_RULE_30_0_1_OK_NAMED_ALIKE_HPP

#include <array>
#include <charconv>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace kv::rule_30_0_1::ok_named_alike {

class Log {
 public:
  void puts(std::string_view text) { last_ = text; }
  void print(std::uint32_t value) {
    const std::to_chars_result r = std::to_chars(digits_.begin(), digits_.end(), value);
    last_ = std::string_view{digits_.data(), static_cast<std::size_t>(r.ptr - digits_.data())};
  }
  [[nodiscard]] std::string_view last() const { return last_; }

 private:
  std::array<char, 16U> digits_{};
  std::string_view last_{};
};

}  // namespace kv::rule_30_0_1::ok_named_alike

#endif  // KV_RULE_30_0_1_OK_NAMED_ALIKE_HPP
