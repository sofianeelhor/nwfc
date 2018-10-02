#---------------------------------------------------------------------------------
.SUFFIXES:
#---------------------------------------------------------------------------------

ifeq ($(strip $(DEVKITARM)),)
$(error "sourcer devkitpro/devkitARM d'abord")
endif

TOPDIR ?= $(CURDIR)
include $(DEVKITARM)/3ds_rules

#---------------------------------------------------------------------------------
TARGET		:=	nwfc
#TARGET		:=	gtsd
BUILD		:=	build
SOURCES		:=	source
DATA		:=	data
INCLUDES	:=	include

APP_TITLE	:=	nwfc
APP_DESCRIPTION	:=	nintendo wfc re
APP_AUTHOR	:=	sofianeelhor

#---------------------------------------------------------------------------------
# options for code generation
#---------------------------------------------------------------------------------
ARCH	:=	-march=armv6k -mtune=mpcore -mfloat-abi=hard -mtp=soft

CFLAGS	:=	-g -Wall -O2 -mword-relocations \
			-fomit-frame-pointer -ffunction-sections \
			$(ARCH)

CFLAGS	+=	$(INCLUDE) -DARM11 -D_3DS

CXXFLAGS	:= $(CFLAGS) -fno-rtti -fno-exceptions -std=gnu++11

ASFLAGS	:=	-g $(ARCH)
LDFLAGS	=	-specs=3dsx.specs -g $(ARCH) -Wl,-Map,$(notdir $*.map)

LIBS	:= -lctru -lm

LIBDIRS	:= $(CTRULIB)

#---------------------------------------------------------------------------------
ifneq ($(BUILD),$(notdir $(CURDIR)))
#---------------------------------------------------------------------------------

export OUTPUT	:=	$(CURDIR)/$(TARGET)
export TOPDIR	:=	$(CURDIR)

export VPATH	:=	$(foreach dir,$(SOURCES),$(CURDIR)/$(dir)) \
			$(foreach dir,$(DATA),$(CURDIR)/$(dir))

export DEPSDIR	:=	$(CURDIR)/$(BUILD)

CFILES		:=	$(foreach dir,$(SOURCES),$(notdir $(wildcard $(dir)/*.c)))
CPPFILES	:=	$(foreach dir,$(SOURCES),$(notdir $(wildcard $(dir)/*.cpp)))
SFILES		:=	$(foreach dir,$(SOURCES),$(notdir $(wildcard $(dir)/*.s)))

export OFILES	:=	$(CPPFILES:.cpp=.o) $(CFILES:.c=.o) $(SFILES:.s=.o)

export INCLUDE	:=	$(foreach dir,$(INCLUDES),-I$(CURDIR)/$(dir)) \
			$(foreach dir,$(LIBDIRS),-I$(dir)/include) \
			-I$(CURDIR)/$(BUILD)

export LIBPATHS	:=	$(foreach dir,$(LIBDIRS),-L$(dir)/lib)

.PHONY: $(BUILD) clean all

all: $(BUILD)

$(BUILD):
	@[ -d $@ ] || mkdir -p $@
	@$(MAKE) --no-print-directory -C $(BUILD) -f $(CURDIR)/Makefile

clean:
	@echo clean ...
	@rm -fr $(BUILD) $(TARGET).3dsx $(OUTPUT).smdh $(TARGET).elf

#---------------------------------------------------------------------------------
else
#---------------------------------------------------------------------------------

DEPENDS	:=	$(OFILES:.o=.d)

$(OUTPUT).3dsx	:	$(OUTPUT).elf $(OUTPUT).smdh
$(OUTPUT).elf	:	$(OFILES)

%.o	:	%.c
	@echo $(notdir $<)
	@$(CC) $(CFLAGS) -MMD -MP -MF $(DEPSDIR)/$*.d $(OUTPUT).elf -c $< -o $@

-include $(DEPENDS)

#---------------------------------------------------------------------------------
endif
#---------------------------------------------------------------------------------
