use std::{any::type_name};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use serde::de::DeserializeOwned;

use cosmwasm_std::{CanonicalAddr, Storage, ReadonlyStorage, StdResult, StdError};
use cosmwasm_storage::{singleton, singleton_read, ReadonlySingleton, Singleton};
use secret_toolkit::serialization::{Bincode2, Serde};

use crate::msg::{CounterIdType};

pub static CONFIG_KEY: &[u8] = b"$config$";
pub static COUNTER_KEY: &[u8] = b"$counter$";

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, JsonSchema)]
pub struct Config {
    pub owner: CanonicalAddr,
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, JsonSchema)]
pub struct Counter {
    pub count: u64,
}

pub fn config_get<S: Storage>(storage: &mut S) -> Singleton<S, Config> {
    singleton(storage, CONFIG_KEY)
}

pub fn config_read<S: Storage>(storage: &S) -> ReadonlySingleton<S, Config> {
    singleton_read(storage, CONFIG_KEY)
}


pub fn GetFullKey(key: CounterIdType) -> Vec<u8> {
    let keySerialized = key.to_be_bytes();
    let fullKey: Vec<u8> = [COUNTER_KEY, &keySerialized].concat();
    fullKey
}

// Save will save if it is not a new value
//
pub fn update<S: Storage>(storage: &mut S, key: CounterIdType, value: &Counter) -> StdResult<()> {
    let fullKey: &[u8] = &GetFullKey(key);
    let result: Option<Counter> = may_load(&*storage, key).ok().unwrap();
    match result {
        Some(_) => {
            storage.set(fullKey, &Bincode2::serialize(&value)?);
            Ok(())
        }
        None => {
            Err(StdError::Unauthorized{backtrace: None})
        }
    }
}

pub fn register<S: Storage>(storage: &mut S, key: CounterIdType, value: &Counter) -> StdResult<()> {
    let fullKey: &[u8] = &GetFullKey(key);
    let result: Option<Counter> = may_load(&*storage, key).ok().unwrap();
    match result {
        Some(_) => {
            Err(StdError::Unauthorized{backtrace: None})
        }
        None => {
            storage.set(fullKey, &Bincode2::serialize(&value)?);
            Ok(())
        }
    }
}

pub fn load<S: ReadonlyStorage>(storage: &S, key: CounterIdType) -> StdResult<Counter> {
    let fullKey: &[u8] = &GetFullKey(key);
    Bincode2::deserialize(
        &storage
            .get(fullKey)
            .ok_or_else(|| StdError::not_found(type_name::<Counter>()))?,
    )
}

pub fn may_load<S: ReadonlyStorage>(storage: &S, key: CounterIdType) -> StdResult<Option<Counter>> {
    let fullKey: &[u8] = &GetFullKey(key);
    match storage.get(fullKey) {
        Some(value) => Ok(Some(Bincode2::deserialize(&value).ok().unwrap())),
        None => Ok(None),
    }
}