// A counter with a ceiling (layering fixture). Not virtual: the word in this comment is not code.
#pragma once

#include <cstdint>

namespace core {

class Counter {
 public:
  explicit Counter(std::uint32_t ceiling) noexcept : ceiling_(ceiling) {}
  bool Increment() noexcept;
  std::uint32_t Value() const noexcept { return value_; }

 private:
  std::uint32_t ceiling_;
  std::uint32_t value_ = 0U;
};

}  // namespace core
