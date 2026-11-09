// Compliant with KB-CPP-046: the Result template and its void specialisation are [[nodiscard]].
#ifndef KV_KB_CPP_046_OK_HPP
#define KV_KB_CPP_046_OK_HPP

#include <cstdint>

namespace kv::kb_cpp_046::ok {

enum class Error : std::uint8_t { kNone, kBus };

template <typename T>
struct [[nodiscard]] Result {
  T value{};
  Error error{Error::kNone};
};

template <>
struct [[nodiscard]] Result<void> {
  Error error{Error::kNone};
};

// Near miss: not a Result type, so the rule does not ask for [[nodiscard]].
struct ResultCode {
  std::uint8_t raw{0U};
};

[[nodiscard]] inline Result<std::uint16_t> read_raw(ResultCode code) {
  return Result<std::uint16_t>{static_cast<std::uint16_t>(code.raw), Error::kNone};
}

[[nodiscard]] inline bool ok(const Result<std::uint16_t>& r, const Result<void>& s) {
  return (r.error == Error::kNone) && (s.error == Error::kNone) && (r.value != 0U);
}

}  // namespace kv::kb_cpp_046::ok

#endif  // KV_KB_CPP_046_OK_HPP
